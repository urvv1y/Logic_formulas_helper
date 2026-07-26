from flask import Flask, render_template_string, request
import main_logic as main
import json
import os

app = Flask(__name__)
FORMULAS_FILE = "saved_formulas.json"

def get_saved_formulas():
    """Loads formulas"""
    if os.path.exists(FORMULAS_FILE):
            try:
                with open(FORMULAS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return []
    return []

def save_formulas_to_file(formulas):
    """Saves formulas"""
    saved = set(get_saved_formulas())
    added = False
    
    for f in formulas:
        f_stripped = f.strip()
        if f_stripped and f_stripped not in saved:
            saved.add(f_stripped)
            added = True
            
    if added:
        with open(FORMULAS_FILE, 'w', encoding='utf-8') as f:
            json.dump(sorted(list(saved)), f, ensure_ascii=False, indent=4)

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
        
        button { padding: 10px 20px; color: white; border: none; border-radius: 4px; font-size: 1em; cursor: pointer; transition: 0.2s; margin-right: 10px; margin-bottom: 10px; }
        .btn-primary { background-color: #808000; }
        .btn-primary:hover { background-color: #6b6b00; }
        .btn-secondary { background-color: #6c757d; }
        .btn-secondary:hover { background-color: #5a6268; }
        .btn-info { background-color: #17a2b8; }
        .btn-info:hover { background-color: #138496; }
        
        .check-btn { background-color: #2196F3; margin-top: 20px; font-size: 1.1em; }
        .check-btn:hover { background-color: #0b7dda; }
        
        table { border-collapse: collapse; margin-bottom: 40px; text-align: center; background-color: #fff; }
        th, td { border: 2px solid #808000; padding: 8px 15px; transition: background-color 0.3s; }
        th { font-style: italic; font-family: "Times New Roman", serif; font-size: 1.2em; }
        
        tr:hover th, tr:hover td { border-color: #2196F3; background-color: #e3f2fd !important; color: #000; }
        tr:first-child:hover th { border-color: #808000; background-color: #fff !important; }
        
        .cell-correct { background-color: #d4edda !important; }
        .cell-incorrect { background-color: #f8d7da !important; }
        
        .logic-input { width: 30px; height: 30px; text-align: center; font-size: 1.2em; font-weight: bold; border: 1px solid #999; border-radius: 4px; background-color: #fff; }
        .logic-input:focus { outline: 2px solid #2196F3; background-color: #eef; }
        td:has(.logic-input) { background-color: #f7f7f7; }
        
        #feedback-area { margin-top: 20px; padding: 15px 20px; border-radius: 5px; font-size: 1.1em; display: none; line-height: 1.6; }
        .feedback-success { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .feedback-warning { background-color: #fff3cd; color: #856404; border: 1px solid #ffeeba; }
        
        .alert-success { background-color: #d4edda; color: #155724; padding: 10px; border-radius: 4px; margin-top: 15px; display: inline-block; }

        p.instruction { font-size: 1.1em; margin-bottom: 10px; font-weight: bold; }
        .legend { font-size: 0.9em; color: #666; margin-top: -10px; margin-bottom: 15px; }
    </style>
</head>
<body>
    <h2>Nastavení formulí</h2>
    
    <datalist id="saved-formulas">
        {% for formula in saved_formulas %}
            <option value="{{ formula }}">
        {% endfor %}
    </datalist>

    <form method="POST" class="settings-form">
        <p class="legend">Nápověda pro symboly: napište <strong>!</strong> pro ¬, <strong>&amp;</strong> pro ∧, <strong>|</strong> pro ∨, <strong>-&gt;</strong> pro ⇒, <strong>&lt;-&gt;</strong> pro ⇔</p>
        
        <div class="form-row">
            <label>Počet proměnných (1-26):</label>
            <input type="number" name="var_count" min="1" max="26" value="{{ var_count }}">
        </div>
        <div class="form-row">
            <label>Formule 1 (1. tabulka):</label>
            <input type="text" id="f1-input" name="f1" value="{{ f1 }}" oninput="replaceSymbols(this)" list="saved-formulas" autocomplete="off">
        </div>
        <div class="form-row">
            <label>Formule 2 (1. tabulka):</label>
            <input type="text" id="f2-input" name="f2" value="{{ f2 }}" oninput="replaceSymbols(this)" list="saved-formulas" autocomplete="off">
        </div>
        <div class="form-row">
            <label>Složená formule (2. tabulka):</label>
            <input type="text" id="f3-input" name="f3" value="{{ f3 }}" oninput="replaceSymbols(this)" list="saved-formulas" autocomplete="off">
        </div>
        
        <div>
            <button type="submit" name="action" value="generate" class="btn-primary">Vygenerovat tabulky</button>
            <button type="button" class="btn-info" onclick="fillRandomFormulas()">Náhodně vybrat z uložených</button>
            <button type="submit" name="action" value="save" class="btn-secondary">Uložit zadané formule</button>
        </div>
        
        {% if save_message %}
            <div class="alert-success">✓ {{ save_message }}</div>
        {% endif %}
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
                        <td><input type="text" class="logic-input" data-correct="{{ correct_ans }}" maxlength="1" oninput="moveToNext(this)"></td>
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
                        <td><input type="text" class="logic-input" data-correct="{{ correct_ans }}" maxlength="1" oninput="moveToNext(this)"></td>
                    {% else %}
                        <td>{{ cell }}</td>
                    {% endif %}
                {% endif %}
            {% endfor %}
            </tr>
        {% endfor %}
    </table>

    <button type="button" class="check-btn" onclick="checkAnswers()">Zkontrolovat správnost</button>
    
    <div id="feedback-area"></div>

    <script>
        
        const savedFormulasList = {{ saved_formulas | tojson }};

        function fillRandomFormulas() {
            if (!savedFormulasList || savedFormulasList.length === 0) {
                alert("Zatím nemáte uložené žádné formule.");
                return;
            }
            
           
            const getRandomFormula = () => {
                const randomIndex = Math.floor(Math.random() * savedFormulasList.length);
                return savedFormulasList[randomIndex];
            };

          
            document.getElementById('f1-input').value = getRandomFormula();
            document.getElementById('f2-input').value = getRandomFormula();
            document.getElementById('f3-input').value = getRandomFormula();
        }

        function replaceSymbols(input) {
            let val = input.value;
            val = val.replace(/<->/g, '⇔').replace(/->/g, '⇒').replace(/&/g, '∧').replace(/\\|/g, '∨').replace(/!/g, '¬');
            if (val !== input.value) { input.value = val; }
        }

        function moveToNext(input) {
            if (input.value !== '0' && input.value !== '1') {
                input.value = '';
                return;
            }
            const inputs = Array.from(document.querySelectorAll('.logic-input'));
            const currentIndex = inputs.indexOf(input);
            if (currentIndex > -1 && currentIndex < inputs.length - 1) {
                inputs[currentIndex + 1].focus();
            }
        }

        function checkAnswers() {
            const inputs = document.querySelectorAll('.logic-input');
            let correctCount = 0;
            let totalCount = 0;
            let hasError = false; 
            
            inputs.forEach(input => {
                const correctAns = input.getAttribute('data-correct');
                const td = input.closest('td');
                td.classList.remove('cell-correct', 'cell-incorrect'); 
                
                if (correctAns === "") { hasError = true; return; }
                
                totalCount++;
                if (input.value === correctAns) {
                    correctCount++;
                    td.classList.add('cell-correct');
                } else {
                    td.classList.add('cell-incorrect');
                }
            });
            
            const feedbackArea = document.getElementById('feedback-area');
            feedbackArea.style.display = 'block';
            feedbackArea.className = ''; 
            
            if (hasError) {
                feedbackArea.innerHTML = "<strong>Chyba:</strong> Některé z vašich formulí obsahují syntaktickou chybu.";
                feedbackArea.classList.add('feedback-warning');
                return;
            }
            
            let table2Analysis = "";
            const table2Inputs = document.querySelectorAll('table:nth-of-type(2) .logic-input');
            if (table2Inputs.length > 0) {
                let ones = 0;
                let zeros = 0;
                table2Inputs.forEach(inp => {
                    const ans = inp.getAttribute('data-correct');
                    if (ans === '1') ones++;
                    if (ans === '0') zeros++;
                });
                if (ones === table2Inputs.length) table2Analysis = "<span style='color:#155724;'><strong>TAUTOLOGIE</strong> (vždy pravdivá)</span>";
                else if (zeros === table2Inputs.length) table2Analysis = "<span style='color:#721c24;'><strong>KONTRADIKCE</strong> (vždy nepravdivá)</span>";
                else table2Analysis = "<strong>SPLNITELNÁ FORMULE</strong> (někdy pravdivá, někdy nepravdivá)";
            }

            let percentage = totalCount > 0 ? Math.round((correctCount / totalCount) * 100) : 0;
            let htmlContent = `<strong>Úspěšnost:</strong> ${correctCount} z ${totalCount} správně (${percentage} %)<br>`;
            if (table2Analysis !== "") htmlContent += `<strong>Analýza složené formule:</strong> Vyhodnocovaná formule je ${table2Analysis}.`;
            
            feedbackArea.innerHTML = htmlContent;
            if (correctCount === totalCount && totalCount > 0) feedbackArea.classList.add('feedback-success');
            else feedbackArea.classList.add('feedback-warning');
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

        action = request.form.get('action')
        if action == 'save':
            save_formulas_to_file([f1, f2, f3])
            save_message = "Formule uloženy"
    
    base_table = main.fill_the_table(var_count)
    
    t1 = base_table
    if f1.strip(): 
        t1 = add_evaluated_formula(t1, f1)
    if f2.strip():
        t1 = add_evaluated_formula(t1, f2)
        
    t2 = base_table
    if f3.strip():
        t2 = add_evaluated_formula(t2, f3)
    saved_formulas = get_saved_formulas()
    
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