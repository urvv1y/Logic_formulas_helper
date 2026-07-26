import main_logic as main


user_variable_count: int = input("Enter the number of variables (1-26): ")
table = main.fill_the_table(int(user_variable_count))
main.print_table(table)

new_table =main.expand_table_by_new_variable(table, "D")
main.print_table(new_table)

expanded = main.expand_table_by_logical_formula(new_table, "A and B")
main.print_table(expanded)

expanded = main.expand_table_by_logical_formula(expanded, "C or D")
main.print_table(expanded)

