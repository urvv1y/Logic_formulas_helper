from flask import Flask, render_template_string, request
import main_logic as main

app = Flask(__name__)

class LogicVar:
    """Evaluator"""
    def __init__(self, val):
        self.val = bool(int(val))

    def __invert__(self):
        return LogicVar(not self.val) # NOT
    
    def __and__(self, other):
        return LogicVar(self.val and other.val) # AND

    def __or__(self, other):
        return LogicVar(self.val or other.val) # OR

    def __le__(self, other):
        return LogicVar((not self.val) or other.val) # ->

    def __eq__(self, other):
        return LogicVar(self.val == other.val) # <->

def evaluate_formula(formula_str, headers, row_values):
    py_form = formula_str.replace('⇔', ' == ') \
                         .replace('⇒', ' <= ') \
                         .replace('∧', ' & ') \
                         .replace('∨', ' | ') \
                         .replace('¬', ' ~ ')
    
    variables = {}
    for h, v in zip(headers, row_values):
        if not h.startswith('!') and v in ('0', '1'):
            variables[h] = LogicVar(v)    
    try:
        res = eval(py_form, {"__builtins__": {}}, variables)
        return "1" if res.val else "0"
    except Exception:
        return ""

def add_evaluated_formula(table, formula):
    if not table or not formula.strip():
        return table
    headers = table[0]
    new_table = [headers + [formula]]
    
    for row in table[1:]:
        correct_ans = evaluate_formula(formula, headers, row)
        new_table.append(row + [f"INPUT:{correct_ans}"])
        
    return new_table
    
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <title>Procvičování logických formulí</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; color: #333; background-color: #fafafa; }
        .settings-form { background-color: #fff; padding: 20px; border: 1px solid #ddd; border-radius: 8px; margin-bottom: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        .form-row { margin-bottom: 15px; }
        .form-row label { display: inline-block; width: 250px; font-weight: bold; }
        .form-row input[type="text"], .form-row input[type="number"] { padding: 8px; width: 300px; border: 1px solid #ccc; border-radius: 4px; font-size: 1em; font-family: "Times New Roman", serif; }
        
        button { padding: 10px 20px; background-color: #808000; color: white; border: none; border-radius: 4px; font-size: 1em; cursor: pointer; transition: 0.2s; }
        button:hover { background-color: #6b6b00; }
        
        .check-btn { background-color: #2196F3; margin-top: 20px; font-size: 1.1em; }
        .check-btn:hover { background-color: #0b7dda; }
        
        table { border-collapse: collapse; margin-bottom: 40px; text-align: center; background-color: #fff; }
        th, td { border: 2px solid #808000; padding: 8px 15px; transition: background-color 0.3s; }
        th { font-style: italic; font-family: "Times New Roman", serif; font-size: 1.2em; }
        td:has(.radio-group) { background-color: #f7f7f7; }
        
        
        .cell-correct { background-color: #d4edda !important; }
        .cell-incorrect { background-color: #f8d7da !important; }
        
        .radio-group { display: inline-flex; gap: 5px; align-items: center; color: #555; }
        .radio-group input { margin: 0 2px 0 5px; cursor: pointer; }
        p.instruction { font-size: 1.1em; margin-bottom: 10px; font-weight: bold; }
        .legend { font-size: 0.9em; color: #666; margin-top: -10px; margin-bottom: 15px; }

        r:hover th, 
        tr:hover td {
            border-color: #2196F3; 
            background-color: #e3f2fd !important; 
            color: #000; 
        }
        
       
        tr:first-child:hover th {
            border-color: #808000;
            background-color: #fff !important;
        }

    </style>
</head>
<body>
    <h2>Nastavení formulí</h2>
    <form method="POST" class="settings-form">
        <p class="legend">Nápověda pro symboly: napište <strong>!</strong> pro ¬, <strong>&amp;</strong> pro ∧, <strong>|</strong> pro ∨, <strong>-&gt;</strong> pro ⇒, <strong>&lt;-&gt;</strong> pro ⇔</p>
        
        <div class="form-row">
            <label>Počet proměnných (1-26):</label>
            <input type="number" name="var_count" min="1" max="26" value="{{ var_count }}">
        </div>
        <div class="form-row">
            <label>Formule 1 (1. tabulka):</label>
            <input type="text" name="f1" value="{{ f1 }}" oninput="replaceSymbols(this)">
        </div>
        <div class="form-row">
            <label>Formule 2 (1. tabulka):</label>
            <input type="text" name="f2" value="{{ f2 }}" oninput="replaceSymbols(this)">
        </div>
        <div class="form-row">
            <label>Složená formule (2. tabulka):</label>
            <input type="text" name="f3" value="{{ f3 }}" oninput="replaceSymbols(this)">
        </div>
        <button type="submit">Vygenerovat tabulky</button>
    </form>

    <p class="instruction">a) V první tabulce vyplňte (zvlášť) vyhodnocení dvou jednoduchých formulí:</p>
    <table>
        {% for row in table1 %}
            <tr>
            {% set r_idx = loop.index0 %}
            {% for cell in row %}
                {% if r_idx == 0 %}
                    <th>{{ cell }}</th>
                {% else %}
                    {% if cell.startswith("INPUT:") %}
                        {% set correct_ans = cell.split(":")[1] %}
                        <td>
                            <div class="radio-group" data-correct="{{ correct_ans }}">
                                <input type="radio" name="t1_r{{r_idx}}_c{{loop.index0}}" value="0"> 0
                                <input type="radio" name="t1_r{{r_idx}}_c{{loop.index0}}" value="1"> 1
                            </div>
                        </td>
                    {% else %}
                        <td>{{ cell }}</td>
                    {% endif %}
                {% endif %}
            {% endfor %}
            </tr>
        {% endfor %}
    </table>

    <p class="instruction">b) V druhé tabulce pak vyplňte vyhodnocení formule složené z předchozích dvou:</p>
    <table>
        {% for row in table2 %}
            <tr>
            {% set r_idx = loop.index0 %}
            {% for cell in row %}
                {% if r_idx == 0 %}
                    <th>{{ cell }}</th>
                {% else %}
                    {% if cell.startswith("INPUT:") %}
                        {% set correct_ans = cell.split(":")[1] %}
                        <td>
                            <div class="radio-group" data-correct="{{ correct_ans }}">
                                <input type="radio" name="t2_r{{r_idx}}_c{{loop.index0}}" value="0"> 0
                                <input type="radio" name="t2_r{{r_idx}}_c{{loop.index0}}" value="1"> 1
                            </div>
                        </td>
                    {% else %}
                        <td>{{ cell }}</td>
                    {% endif %}
                {% endif %}
            {% endfor %}
            </tr>
        {% endfor %}
    </table>

    <button type="button" class="check-btn" onclick="checkAnswers()">Zkontrolovat správnost</button>

    <script>
        function replaceSymbols(input) {
            let val = input.value;
            val = val.replace(/<->/g, '⇔').replace(/->/g, '⇒').replace(/&/g, '∧').replace(/\\|/g, '∨').replace(/!/g, '¬');
            if (val !== input.value) { input.value = val; }
        }

        function checkAnswers() {
            let allCorrect = true;
            let answeredAny = false;
            let hasError = false; 
            
            const groups = document.querySelectorAll('.radio-group');
            
            groups.forEach(group => {
                const correctAns = group.getAttribute('data-correct');
                const td = group.closest('td');
                td.classList.remove('cell-correct', 'cell-incorrect'); 
                
                if (correctAns === "") {
                    hasError = true;
                    return; 
                }
                
                const selected = group.querySelector('input[type="radio"]:checked');
                
                if (selected) {
                    answeredAny = true;
                    if (selected.value === correctAns) {
                        td.classList.add('cell-correct');
                    } else {
                        td.classList.add('cell-incorrect');
                        allCorrect = false;
                    }
                } else {
                    td.classList.add('cell-incorrect'); 
                    allCorrect = false;
                }
            });
            
            if (hasError) {
                alert("Některé z vašich formulí obsahují syntaktickou chybu (např. chybějící závorka), systém je nemohl vyhodnotit.");
            } else if (allCorrect && answeredAny) {
                alert("Výborně! Všechny hodnoty jsou správně.");
            } else if (!answeredAny) {
                alert("Nejprve musíte vyplnit nějaké hodnoty.");
            }
        }
    </script>
</body>
</html>
"""


def format_logic_symbols(formula: str) -> str:
    return formula.replace('<->', '⇔') \
                  .replace('->', '⇒') \
                  .replace('&', '∧') \
                  .replace('|', '∨') \
                  .replace('!', '¬')

@app.route('/', methods=['GET', 'POST'])
def index():

    var_count = 3
    f1 = "(X ∧ ¬Y)"
    f2 = "¬(Z ∧ X)"
    f3 = "(X ∧ ¬Y) ⇒ ¬(Z ∧ X)"

    if request.method == 'POST':
        try:
            var_count = int(request.form.get('var_count', 3))
        except ValueError:
            var_count = 3
            
        f1 = format_logic_symbols(request.form.get('f1', ''))
        f2 = format_logic_symbols(request.form.get('f2', ''))
        f3 = format_logic_symbols(request.form.get('f3', ''))

    
    base_table = main.fill_the_table(var_count)
    
    
    t1 = base_table
    if f1.strip(): 
        t1 = add_evaluated_formula(t1, f1)
    if f2.strip():
        t1 = add_evaluated_formula(t1, f2)
        
    
    t2 = base_table
    if f3.strip():
        t2 = add_evaluated_formula(t2, f3)
    
    
    return render_template_string(
        HTML_TEMPLATE, 
        table1=t1, 
        table2=t2,
        var_count=var_count,
        f1=f1, 
        f2=f2, 
        f3=f3
    )

if __name__ == '__main__':
    app.run(debug=True)