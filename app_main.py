import main_logic as main


user_variable_count: int = input("Enter the number of variables (1-26): ")
table = main.fill_the_table(int(user_variable_count))
main.print_table(table)

