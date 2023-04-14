import os
import json
from fal import FalDbt

from column_lineage import ColumnLineage
from utils import _preprocess_sql
from typing import List
from itertools import islice
# for key, value in islice(manifest['nodes'].items(), 3):


class Lineage:
    def __init__(self, path: str = None, profiles_dir: str = "~/.dbt"):
        if path is None:
            raise Exception("Path not specified.")
        f = open(os.path.join(path, "target", "manifest.json"))
        self.manifest = json.load(f)
        self.faldbt = FalDbt(profiles_dir=profiles_dir, project_dir=path)
        # self.table_cols_df = self.faldbt.execute_sql(
        #     """SELECT attrelid::regclass AS table, string_agg(attname, ', ')  AS col
        # FROM   pg_attribute
        # WHERE  attnum > 0
        # AND    NOT attisdropped
        # GROUP BY attrelid::regclass
        # ORDER  BY attrelid::regclass;"""
        # )
        self.output_dict = {}
        self._run_lineage()

    def _run_lineage(self) -> None:
        """
        Start the column lineage call
        :return: the output_dict object will be the final output with each model name being key
        """
        self.part_tables = self._get_part_tables()
        key = 'model.mimic.age_histogram'
        value = self.manifest['nodes'][key]
        #for key, value in self.manifest["nodes"].items():
        #for key, value in islice(self.manifest['nodes'].items(), 3):
        print(key)
        table_name = value["schema"] + "." + value["name"]
        self.output_dict[key] = {}
        self.output_dict[key]["sql"] = value["compiled_code"]
        ret_sql = _preprocess_sql(value)
        ret_fal = self.faldbt.execute_sql(
            "EXPLAIN (VERBOSE TRUE, FORMAT JSON, COSTS FALSE) {}".format(ret_sql)
        )
        plan = json.loads(ret_fal.iloc[0]["QUERY PLAN"][1:-1])
        col_names = self._find_column(table_name=table_name)
        #col_names_new = self.table_cols_df[self.table_cols_df["table"] == table_name]
        #print(self.table_cols_df, col_names)
        col_lineage = ColumnLineage(
            plan=plan["Plan"],
            sql=ret_sql,
            cols=col_names,
            faldbt=self.faldbt,
            part_tables=self.part_tables,
        )
        self.output_dict[key]["tables"] = col_lineage.table_list
        self.output_dict[key]["columns"] = col_lineage.column_dict
        self.output_dict[key]["table_name"] = table_name
        self.output_dict[key]["plan"] = plan["Plan"]

    def _get_part_tables(self) -> dict:
        """
        Find the partitioned table and their parents, so that the final output would only show the parent table name
        :return: a dict with child being key and parent being the value
        """
        parent_fal = self.faldbt.execute_sql(
            """SELECT
                    concat_ws('.', nmsp_parent.nspname, parent.relname) AS parent,
                    concat_ws('.', nmsp_child.nspname, child.relname) AS child
                FROM pg_inherits
                    JOIN pg_class parent            ON pg_inherits.inhparent = parent.oid
                    JOIN pg_class child             ON pg_inherits.inhrelid   = child.oid
                    JOIN pg_namespace nmsp_parent   ON nmsp_parent.oid  = parent.relnamespace
                    JOIN pg_namespace nmsp_child    ON nmsp_child.oid   = child.relnamespace"""
        )
        return dict(zip(parent_fal.child, parent_fal.parent))

    def _find_column(self, table_name: str = "") -> List:
        """
        Find the columns for the base table in the database
        :param table_name: the base table name
        :return: the list of columns in the base table
        """
        cols_fal = self.faldbt.execute_sql(
            """SELECT attname AS col
        FROM   pg_attribute
        WHERE  attrelid = '{}'::regclass  -- table name optionally schema-qualified
        AND    attnum > 0
        AND    NOT attisdropped
        ORDER  BY attnum;
         ;""".format(
                table_name
            )
        )
        return list(cols_fal["col"])

if __name__ == "__main__":
    print(os.getcwd())
    lineage_output = Lineage("D:\\Archive - Copy")
    with open("table_output.json", "w") as outfile:
        json.dump(lineage_output.output_dict, outfile)
    #dag_nodes, column_list = draw_lineage(lineage_output.output_dict['model.mimic.echo_data'], lineage_output.manifest["nodes"]['model.mimic.echo_data'])
    #print(dag_nodes, column_list)
