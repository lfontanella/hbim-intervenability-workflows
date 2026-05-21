import logging
import __main__
import sys
import pandas as pd
import json
import os
import copy
import random
import numpy as np

import ast
import operator as op
import math

random.seed(1)

_MISSING_STRINGS = {"", " ", "nan", "NaN", "NAN", "null", "NULL", "None", "NONE", "-"}

def is_missing(x) -> bool:
    if x is None:
        return True
    try:
        if pd.isna(x):
            return True
    except Exception:
        pass
    if isinstance(x, str):
        return x.strip() in _MISSING_STRINGS
    return False

def as_clean_str(x) -> str:
    if x is None:
        return ""
    if isinstance(x, str):
        return x.strip()
    return str(x)

def clamp(x, lo, hi):
    return max(lo, min(hi, x))

def hex_to_rgb(h: str):
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

def inv_to_turbo_hex(inv_value: float, inv_min: float, inv_max: float, start_idx: int = 100):
    from bokeh.palettes import Turbo256

    if inv_min is None or inv_max is None or inv_min == inv_max:
        idx = clamp(start_idx, 0, 255)
        return Turbo256[idx]

    v = clamp(float(inv_value), float(inv_min), float(inv_max))
    t = (v - float(inv_min)) / (float(inv_max) - float(inv_min))
    idx = int(round(start_idx + t * (255 - start_idx)))
    idx = clamp(idx, start_idx, 255)
    return Turbo256[idx]


class gnrl:
    def __init__(self):
        if getattr(sys, 'frozen', False):
            self.app_folder = os.path.dirname(sys.executable)
        else:
            self.app_folder = os.path.dirname(os.path.abspath(__file__))

    def get_logger(self, name, console_level=logging.INFO, file_level=logging.DEBUG, log_file='app.log'):
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(console_level)
        formatter_console = logging.Formatter(
            '%(asctime)s.%(msecs)03d | %(filename)-24s | %(lineno)05d | %(funcName)-24s | %(levelname)-10s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
        )
        console_handler.setFormatter(formatter_console)

        file_handler = logging.FileHandler(os.path.join(self.app_folder, log_file), delay=False, encoding="utf-8")
        file_handler.setLevel(file_level)
        formatter_file = logging.Formatter(
            '%(asctime)s.%(msecs)03d,%(filename)-24s,%(lineno)05d,%(funcName)-24s,%(levelname)-10s,%(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
        )
        file_handler.setFormatter(formatter_file)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        return logger


class intrvnblt:
    DEFAULT_IF_VALUE_MISSING = False

    def __init__(self, app_folder='?', logger='?'):
        self.app_folder = app_folder
        self.logger = logger
        self.logger.debug('Logger - Started')

        self.start0_file_pathandname = os.path.join(self.app_folder, '..\\START.json')
        self.start0_file_content = json.load(open(self.start0_file_pathandname, encoding="utf-8"))

        self.start_file_pathandname = os.path.join(os.path.join(self.app_folder, '..\\'), self.start0_file_content['start_file_name'])
        self.start_file_content = json.load(open(self.start_file_pathandname, encoding="utf-8"))

        self.logger.debug('start_file_pathandname: %s', self.start_file_pathandname)
        self.logger.debug('start_file_content: %s', str(self.start_file_content))

        self.get_input()
        self.run()

    def get_input(self):
        self.project_code = self.start_file_content['project_code']
        self.input_folder_path = os.path.normpath(os.path.join(self.app_folder, self.start_file_content['input_folder_path']))
        self.output_folder_path = os.path.normpath(os.path.join(self.app_folder, self.start_file_content['output_folder_path']))
        self.queries_sheet_name = self.start_file_content['queries_sheet_name']
        self.elements_sheet_name = self.start_file_content['elements_sheet_name']

        self.excel_file_pathandname = os.path.join(self.input_folder_path, self.start_file_content['input_file_name'])

        self.df_s_query = pd.read_excel(self.excel_file_pathandname, sheet_name=self.queries_sheet_name)
        self.df_s_surface = pd.read_excel(self.excel_file_pathandname, sheet_name=self.elements_sheet_name)
        self.df_s_constraint = pd.read_excel(self.excel_file_pathandname, sheet_name="CONSTRAINTS")
        self.df_s_setting = pd.read_excel(self.excel_file_pathandname, sheet_name="SETTINGS")

        for col in self.df_s_surface.columns:
            if col in ("Code", "Type"):
                continue
            if pd.api.types.is_numeric_dtype(self.df_s_surface[col]):
                self.df_s_surface[col] = self.df_s_surface[col].fillna(0)

        # output in OUT (così Dynamo lo trova dove se lo aspetta)
        os.makedirs(self.output_folder_path, exist_ok=True)
        self.results_xlsx_path = os.path.join(self.output_folder_path, "Intervenability_RESULTS.xlsx")
        self.summary_rows = []
        self.details_rows = []

    def run(self):
        for index, row in self.df_s_query.iterrows():
            self.run_1query(self.df_s_query.to_dict('records')[index])

        self.save_results()

    def run_1query(self, dict_in='?'):
        n_query = dict_in["nQuery"]
        in1 = dict_in["IN[1]"]
        in2 = dict_in["IN[2]"]
        in3 = dict_in["IN[3]"]
        in4 = dict_in["IN[4]"]
        in5 = dict_in["IN[5]"]

        _df_s_surface = copy.deepcopy(self.df_s_surface)
        _df_s_setting_s_column = self.df_s_setting.columns

        # invasività per intervento
        row_invasivity = self.df_s_constraint.loc[self.df_s_constraint['Parameter'] == 'Invasivity'].loc[0].values[1:]
        inv_min = float(min(row_invasivity))
        inv_max = float(max(row_invasivity))
        n_starting_colour = 100

        for index_surface, surface in _df_s_surface.iterrows():
            _df_s_constraint = self.df_s_constraint.set_index('Parameter').transpose()
            _df_s_constraint['IsFeasible'] = False

            invasivity_list = []
            feasible_count = 0

            n_intervention = -1
            for index_intervention, intervention in _df_s_constraint.iterrows():
                n_intervention += 1
                isfeasible = True

                for action in _df_s_constraint.columns[1:-1].to_list():
                    cell = intervention[action]

                    if is_missing(cell):
                        result = True
                    else:
                        if action in _df_s_setting_s_column:
                            matches = self.df_s_setting.loc[self.df_s_setting[action] == surface[action]]['Value'].to_list()
                            value = matches[0] if len(matches) > 0 else np.nan
                        else:
                            value = surface[action] if action in surface.index else np.nan

                        if is_missing(value):
                            result = self.DEFAULT_IF_VALUE_MISSING
                            self.logger.debug(
                                "VALUE missing -> action=%s | surface_index=%s | cell=%s | policy_result=%s",
                                action, index_surface, as_clean_str(cell), result
                            )
                        else:
                            expression = f"{as_clean_str(value)}{as_clean_str(cell)}"
                            try:
                                result = self._safe_eval(
                                    expression,
                                    names={'in1': in1, 'in2': in2, 'in3': in3, 'in4': in4, 'in5': in5}
                                )
                            except Exception as e:
                                result = False
                                self.logger.debug("EVAL error -> action=%s | expr=%s | err=%s", action, expression, repr(e))

                    isfeasible = bool(isfeasible) and bool(result)

                _df_s_constraint.loc[index_intervention, 'IsFeasible'] = bool(isfeasible)

                value_inv = max(row_invasivity)
                if isfeasible:
                    value_inv = row_invasivity[n_intervention]
                    feasible_count += 1
                invasivity_list.append(value_inv)

                # DETAILS row
                self.details_rows.append({
                    "nQuery": n_query,
                    "Code": surface.get("Code", ""),
                    "InterventionName": str(index_intervention),
                    "IsFeasible": bool(isfeasible),
                    "Invasivity": float(value_inv) if not is_missing(value_inv) else np.nan
                })

            intervenability = float(min(invasivity_list)) if len(invasivity_list) else float(inv_max)

            colour_hex = inv_to_turbo_hex(intervenability, inv_min, inv_max, start_idx=n_starting_colour)
            r, g, b = hex_to_rgb(colour_hex)

            self.summary_rows.append({
                "nQuery": n_query,
                "Code": surface.get("Code", ""),
                "Type": surface.get("Type", ""),
                "Intervenability": intervenability,
                "ColourHex": colour_hex,
                "R": int(r),
                "G": int(g),
                "B": int(b),
                "FeasibleCount": int(feasible_count)
            })

        self.logger.info("Query %s completata. Righe summary aggiunte: %s", n_query, len(_df_s_surface))

    def save_results(self):
        df_summary = pd.DataFrame(self.summary_rows)
        # garantisco ordine colonne
        wanted = ["nQuery", "Code", "Type", "Intervenability", "FeasibleCount", "ColourHex", "R", "G", "B"]
        for c in wanted:
            if c not in df_summary.columns:
                df_summary[c] = ""
        df_summary = df_summary[wanted]

        df_details = pd.DataFrame(self.details_rows)
        wanted_d = ["nQuery", "Code", "InterventionName", "IsFeasible", "Invasivity"]
        for c in wanted_d:
            if c not in df_details.columns:
                df_details[c] = ""
        df_details = df_details[wanted_d]

        with pd.ExcelWriter(self.results_xlsx_path, engine="openpyxl") as writer:
            df_summary.to_excel(writer, sheet_name="SUMMARY", index=False)
            df_details.to_excel(writer, sheet_name="DETAILS", index=False)

        self.logger.info("Salvato Excel risultati: %s", self.results_xlsx_path)

    def _safe_eval(self, expr: str, names: dict):
        _ALLOWED_OPS = {
            ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv,
            ast.FloorDiv: op.floordiv, ast.Mod: op.mod, ast.Pow: op.pow,
            ast.UAdd: op.pos, ast.USub: op.neg,
            ast.Eq: op.eq, ast.NotEq: op.ne, ast.Lt: op.lt, ast.LtE: op.le,
            ast.Gt: op.gt, ast.GtE: op.ge,
            ast.And: lambda a, b: a and b,
            ast.Or:  lambda a, b: a or b,
        }

        _ALLOWED_NAMES = {
            "pi": math.pi,
            "e": math.e,
            "nan": float("nan"),
            "NaN": float("nan"),
            "abs": abs,
            "round": round,
            "min": min,
            "max": max
        }

        _ALLOWED_FUNCS = {"min": min, "max": max, "abs": abs, "round": round}

        def _eval(node):
            if isinstance(node, ast.Expression):
                return _eval(node.body)
            elif isinstance(node, ast.Constant):
                return node.value
            elif isinstance(node, ast.Num):
                return node.n
            elif isinstance(node, ast.Name):
                if node.id in names:
                    return names[node.id]
                if node.id in _ALLOWED_NAMES:
                    return _ALLOWED_NAMES[node.id]
                raise NameError(f"Name not allowed: {node.id}")
            elif isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPS:
                return _ALLOWED_OPS[type(node.op)](_eval(node.operand))
            elif isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPS:
                return _ALLOWED_OPS[type(node.op)](_eval(node.left), _eval(node.right))
            elif isinstance(node, ast.BoolOp) and type(node.op) in _ALLOWED_OPS:
                vals = [_eval(v) for v in node.values]
                out = vals[0]
                for v in vals[1:]:
                    out = _ALLOWED_OPS[type(node.op)](out, v)
                return out
            elif isinstance(node, ast.Compare):
                left = _eval(node.left)
                result = True
                for op_node, comparator in zip(node.ops, node.comparators):
                    if type(op_node) not in _ALLOWED_OPS:
                        raise ValueError("Operator not allowed")
                    right = _eval(comparator)
                    if not _ALLOWED_OPS[type(op_node)](left, right):
                        result = False
                        break
                    left = right
                return result
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in _ALLOWED_FUNCS:
                    fn = _ALLOWED_FUNCS[node.func.id]
                    args = [_eval(a) for a in node.args]
                    if node.keywords:
                        raise ValueError("Keyword arguments non consentiti")
                    return fn(*args)
                raise ValueError("Function not allowed")
            else:
                raise ValueError(f"Construct not allowed: {type(node).__name__}")

        tree = ast.parse(expr, mode="eval")
        return _eval(tree)


if __name__ == '__main__':
    general = gnrl()
    logger = general.get_logger(__name__, console_level=logging.INFO, file_level=logging.DEBUG, log_file='app.log')
    logger.debug('START')
    Intervenability = intrvnblt(app_folder=general.app_folder, logger=logger)
