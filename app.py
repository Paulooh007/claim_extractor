import gradio as gr
from theme import CustomTheme
import pandas as pd
import time
import openai
import os


custom_theme = CustomTheme()


openai.api_key = os.environ.get("OPENAI_API_KEY")

ft_model_ada = "ada:ft-personal-2023-05-17-17-03-33"


def upload_file(file, model_name):
    with open(file.name, "r", encoding="unicode_escape") as f:
        content = f.read().replace("\n", "")

    sentences = list(map(str.strip, content.split(".")))
    df = pd.DataFrame({"claim": sentences}, index=range(len(sentences)))
    # df = pd.DataFrame({"claim": sentences[:10]}, index=range(len(sentences[:10])))

    col = f"openai_pred_{model_name}"
    model = ft_model_ada

    results = []

    start_time = time.time()

    for i in range(len(sentences)):
        res = openai.Completion.create(
            model=model, prompt=sentences[i] + " ->", max_tokens=1, temperature=0
        )
        results.append(res["choices"][0]["text"])

    end_time = time.time()

    # results = sentences[:10]

    df[col] = results
    df[col] = df[col].map({" True": 1, " False": 0})

    time_taken = round(end_time - start_time, 2)

    display_df_openai_ada = df.loc[df[col] == 1]

    return display_df_openai_ada, time_taken


def export_csv(d, file):
    filename = file.name.split("/")[-1].split(".")[0]
    d.to_csv(f"{filename}_output.csv")
    # filename = file.name.split(".")[0]
    return gr.File.update(value=f"{filename}_output.csv", visible=True)


with gr.Blocks(theme=custom_theme) as demo:
    gr.Markdown(value="# Upload transcription txt file")

    with gr.Row():
        input_document_pdf = gr.File(label="Uplaod transcription file")

    with gr.Row():
        with gr.Column():
            model_name_ada = gr.Text(label="model_name", value="ada", visible=False)
            output_df = gr.Dataframe(
                row_count=(2, "dynamic"),
                col_count=(2, "dynamic"),
                headers=["claim", "prediction"],
                label="Predictions",
                wrap=True,
            )

            time_taken = gr.Text(label="Time Taken", lines=1)
            download = gr.Button("Download output", variant="primary")

            csv = gr.File(interactive=False, visible=False)

    input_document_pdf.upload(
        upload_file, [input_document_pdf, model_name_ada], [output_df, time_taken]
    )

    download.click(export_csv, [output_df, input_document_pdf], [csv])


if __name__ == "__main__":
    demo.launch(debug=True)
