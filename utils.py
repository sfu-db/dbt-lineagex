import re
import ast
from typing import Tuple, List


def _remove_comments(str1: str = "") -> str:
    """
    Remove comments/excessive spaces/"create table as"/"create view as" from the sql file
    :param str1: the original sql
    :return: the parsed sql
    """
    # remove the /* */ comments
    q = re.sub(r"/\*[^*]*\*+(?:[^*/][^*]*\*+)*/", "", str1)
    # remove whole line -- and # comments
    lines = [line for line in q.splitlines() if not re.match("^\s*(--|#)", line)]
    # remove trailing -- and # comments
    q = " ".join([re.split("--|#", line)[0] for line in lines])
    # replace all spaces around commas
    q = re.sub(r"\s*,\s*", ",", q)
    # replace all multiple spaces to one space
    str1 = re.sub("\s\s+", " ", q)
    str1 = str1.replace("\n", " ").strip()
    return str1


def _preprocess_sql(node: dict = None) -> str:
    """
    Process the sql, remove database name in the clause/datetime_add/datetime_sub adding quotes
    :param node: the node containing the original sql, file: file name for the sql
    :return: None
    """
    if node is None:
        return ""
    org_sql = node["compiled_code"]
    ret_sql = _remove_comments(str1=org_sql)
    ret_sql = ret_sql.replace("`", "")
    # remove any database names in the query
    schema = node["schema"]
    #     for i in schemas:
    #         ret_sql = re.sub("[^ (,]*(\.{}\.)".format(i), "{}.".format(i), ret_sql)
    ret_sql = re.sub("[^ (,]*(\.{}\.)".format(schema), "{}.".format(schema), ret_sql)
    ret_sql = re.sub(
        r"DATETIME_DIFF\((.+?),\s?(.+?),\s?(DAY|MINUTE|SECOND|HOUR|YEAR)\)",
        r"DATETIME_DIFF(\1, \2, '\3'::TEXT)",
        ret_sql,
    )
    ret_sql = re.sub("datetime_add", "DATETIME_ADD", ret_sql, flags=re.IGNORECASE)
    ret_sql = re.sub("datetime_sub", "DATETIME_SUB", ret_sql, flags=re.IGNORECASE)
    # DATETIME_ADD '' value
    dateime_groups = re.findall(
        r"DATETIME_ADD\(\s?(.+?),\s?INTERVAL\s?(.+?)\s?(DAY|MINUTE|SECOND|HOUR|YEAR)\)",
        ret_sql,
    )
    if dateime_groups:
        for i in dateime_groups:
            if not i[1].startswith("'") and not i[1].endswith("'"):
                ret_sql = ret_sql.replace(
                    "DATETIME_ADD({},INTERVAL {} {})".format(i[0], i[1], i[2]),
                    "DATETIME_ADD({},INTERVAL '{}' {})".format(i[0], i[1], i[2]),
                )
            else:
                continue
    # DATETIME_SUB '' value
    dateime_sub_groups = re.findall(
        r"DATETIME_SUB\(\s?(.+?),\s?INTERVAL\s?(.+?)\s?(DAY|MINUTE|SECOND|HOUR|YEAR)\)",
        ret_sql,
    )
    if dateime_sub_groups:
        for i in dateime_sub_groups:
            if not i[1].startswith("'") and not i[1].endswith("'"):
                ret_sql = ret_sql.replace(
                    "DATETIME_SUB({},INTERVAL {} {})".format(i[0], i[1], i[2]),
                    "DATETIME_SUB({},INTERVAL '{}' {})".format(i[0], i[1], i[2]),
                )
            else:
                continue
    return ret_sql

# def draw_lineage(l, manifest_data):
#     # getting the manifest ref
#     if len(manifest_data['refs']) != 0:
#         ref_list = [manifest_data['schema'] + "." + i[0] for i in manifest_data['refs']]
#     else:
#         ref_list = []
#     # iterate to get tables
#     dag_nodes = [{"data": {"id": l['table_name'],}}]
#     dag_edge_nodes = []
#     column_list = [{"data": {"id": l['table_name'], "type": "Table"}}]
#     column_list_edge = []
#     for idx, t in enumerate(l['tables']):
#         dag_nodes.append({"data": {"id": t,}})
#         dag_edge_nodes.append({"data": {"id": f"e{idx}", "source": str(t), "target": l['table_name'],}})
#         if t in ref_list:
#             column_list.append({"data": {"id": t, "type": "Subquery"}})
#         else:
#             column_list.append({"data": {"id": t, "type": "Table"}})
#     # iterate to get columns
#     edge_num = 0
#     added_nodes = []
#     for target_col, depend_list in l['columns'].items():
#         column_list.append({"data": {"id": f"{l['table_name']}.{target_col}", "parent": l['table_name'], "type": 'Column',}})
#         for depend_col in depend_list:
#             if depend_col not in added_nodes:
#                 added_nodes.append(depend_col)
#                 column_list.append({"data": {"id": f"{depend_col}", "parent": ".".join(depend_col.split(".")[:2]), "type": 'Column',}})
#             column_list_edge.append({"data": {"id": f"e{edge_num}", "source": depend_col, "target": f"{l['table_name']}.{target_col}",}})
#             edge_num += 1
#     return dag_nodes + dag_edge_nodes, column_list + column_list_edge


def draw_lineage(output_data: dict = None, manifest_data: dict = None) -> Tuple[List, List]:
    """
    Parse the information into a format for front-end
    :param output_data:the data in the output_dict
    :param manifest_data: the original manifest_data
    :return:
    """
    # getting the manifest ref
    if len(manifest_data['refs']) != 0:
        ref_list = [manifest_data['schema'] + "." + i[0] for i in manifest_data['refs']]
    else:
        ref_list = []
    # iterate to get tables
    dag_nodes = [{"data": {"id": output_data['table_name'], }}]
    dag_edge_nodes = []
    column_list = [{"data": {"id": output_data['table_name'], "type": "Table"}}]
    column_list_edge = []
    for idx, t in enumerate(output_data['tables']):
        dag_nodes.append({"data": {"id": t, }})
        dag_edge_nodes.append({"data": {"id": f"e{idx}", "source": str(t), "target": output_data['table_name'], }})
        if t in ref_list:
            column_list.append({"data": {"id": t, "type": "Subquery"}})
        else:
            column_list.append({"data": {"id": t, "type": "Table"}})
    # iterate to get columns
    edge_num = 0
    depend_dict = {}
    added_nodes = []
    for target_col, depend_list in output_data['columns'].items():
        if str(depend_list) in depend_dict.keys():
            depend_dict[str(depend_list)].append(target_col)
        else:
            depend_dict[str(depend_list)] = [target_col]

    for depend_list_key, target_col_val in depend_dict.items():
        # Add all base nodes
        for depend_col in ast.literal_eval(depend_list_key):
            if depend_col not in added_nodes:
                added_nodes.append(depend_col)
                column_list.append({"data": {"id": f"{depend_col}", "parent": ".".join(depend_col.split(".")[:2]), "type": 'Column', }})
        # If there are less than 5 columns with the same dependency
        if len(target_col_val) < 5:
            for target_col in target_col_val:
                column_list.append({"data": {"id": f"{output_data['table_name']}.{target_col}", "parent": output_data['table_name'], "type": 'Column', }})
                for depend_col in ast.literal_eval(depend_list_key):
                    column_list_edge.append({"data": {"id": f"e{edge_num}", "source": depend_col, "target": f"{output_data['table_name']}.{target_col}", }})
                    edge_num += 1
        else:
            column_list.append({"data": {"id": f"{output_data['table_name']}.{str(target_col_val[:4]) + '...'}", "parent": output_data['table_name'], "type": 'Column', }})
            for depend_col in ast.literal_eval(depend_list_key):
                column_list_edge.append({"data": {"id": f"e{edge_num}", "source": depend_col, "target": f"{output_data['table_name']}.{str(target_col_val[:4]) + '...'}", }})
                edge_num += 1
    return dag_nodes + dag_edge_nodes, column_list + column_list_edge


if __name__ == "__main__":
    pass
