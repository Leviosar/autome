from tabulate import tabulate


def display_analysis_table(grammar, table):
    return
    print("TABLE")
    headers = ["..."] + grammar.terminals
    data = []

    for row in table:
        data_row = [row]
        for item in table[row]:
            pass
            print(item)

        data.append(data_row)

    print(tabulate(data, headers=headers))
