import pandas as pd


def export_schedule(
        assignments,
        output_file):

    result_df = pd.DataFrame(assignments)

    result_df.to_excel(
        output_file,
        index=False
    )

    return result_df