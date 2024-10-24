import json
import os

import requests
from bs4 import BeautifulSoup
from langchain_community.callbacks import get_openai_callback
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.output_parsers import SimpleJsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI
from openai import AzureOpenAI

from app.configs.config import Config

client = AzureOpenAI(
    azure_endpoint=Config.OPENAI_API_BASE_URL,
    api_version="2024-02-01",
    api_key=Config.OPENAI_API_KEY,
)

model = AzureChatOpenAI(
    azure_endpoint=Config.OPENAI_API_BASE_URL,
    openai_api_version="2024-02-01",
    azure_deployment=Config.MODEL_NAME,
    openai_api_key=Config.OPENAI_API_KEY,
    temperature=Config.TEMPERATURE,
)


def download_image(image_url, save_directory, filename):
    try:
        # Send an HTTP request to the image URL
        response = requests.get(image_url, stream=True)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Ensure the save directory exists
            if not os.path.exists(save_directory):
                os.makedirs(save_directory)

            # Create the full path for saving the image
            image_path = os.path.join(save_directory, filename)

            # Open the file in write-binary mode and write the content
            with open(image_path, "wb") as img_file:
                for chunk in response.iter_content(1024):
                    img_file.write(chunk)

            print(f"Image successfully downloaded: {image_path}")
            return f"./images/{filename}"
        else:
            print(f"Failed to retrieve image. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error occurred: {e}")
        return None


def generate_summary(pdf_content):
    """
    Given a pdf file, return a summarization and its relevent image
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                You are a document summarizer. I will provide you with the content of a PDF file.
                Please summarize the main key points of the document, list them in bullet points, and give a really detailed explaination of each bullet point, try to include the content from the file. Please don't list over 6 points.
                Please summarize the file in the language of the file. For example, if the file is mostly written in traditional chinese, then summarize in traditional chinese.
                """,
            ),
            (
                "user",
                "Summarize the content of this PDF: {data}, please output the summarization in json format, using 'summary' and 'summary-list' as key, and store multiple dictionary in 'summary-list'. For each dictionary, the keys are 'keypoint', 'explaination'. Ex: 'summary': // full document summary, 'summary-list': [dict('keypoint': //keypoint, 'explaination': //explaination), ...]",
            ),
        ]
    )
    chain = prompt | model | SimpleJsonOutputParser()
    summary = chain.invoke({"data": pdf_content})

    return summary


def generate_images(summary_info):

    # Key:Value -> "ImageURL":"Image relative path"
    image_src = dict()

    restriction_text = "No text or words should be visible in the image. Ensure the overall feel is natural, simple and clean, not AI-generated like. If you need to create human, please create real-human like. Create cartoon animated style image describled by the following:"
    # restriction_text = "No text or words should be visible in the image. Ensure the overall feel is natural, simple and clean, not AI-generated like. Create a painting style image describled by the following:"

    # Generate image for summary
    summary_text = summary_info["summary"]

    result = client.images.generate(
        model="dall-e-3", prompt=restriction_text + summary_text, n=1
    )

    summary_url = json.loads(result.model_dump_json())["data"][0]["url"]
    summary_info["summaryimageURL"] = summary_url
    image_src[summary_url] = download_image(
        summary_url, "./Public/images", "summary.png"
    )

    # Geenrate the image for keypoints
    summary_list = summary_info["summary-list"]
    for index, kp in enumerate(summary_list):
        kp_text = kp["keypoint"] + ". " + kp["explaination"]
        try:
            kp_result = client.images.generate(
                model="dall-e-3", prompt=restriction_text + kp_text, n=1
            )
        except Exception as e:
            print(f"Exception: {e}")
            kp_result = client.images.generate(
                model="dall-e-3", prompt=e["revised_prompt"], n=1
            )
        image_url = json.loads(kp_result.model_dump_json())["data"][0]["url"]
        kp["imageURL"] = image_url
        image_src[image_url] = download_image(
            image_url, "./Public/images", f"keypoint{index}.png"
        )

    return summary_info, image_src


def generate_html(content, summary_info, user_input):

    # Open and read an template HTML file
    with open("./template/template1.html", "r", encoding="utf-8") as file:
        html_template = file.read()

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                You are a fantastic web programmer. I will provide you with the summarization of the PDF file and the style of the user needs.
                Please modify the html template to show the summarization of the pdf according to the summarization I provided. Also include the summary image using the 'summaryImageURL' in the 'summary_info' variable. Also include the images of each keypoints.
                Based on the user's input, modify the HTML template, with the summarizations of the pdf according to the summarization I provided. 
                For each keypoint, please generate one section in the html. 
                Only output the html please and make sure the html code syntax is correct.
                Output example: '<!DOCTYPE html>.....'
                """,
            ),
            (
                "user",
                "This is the summary_info: {summary_info}. This is the HTML template: {html_template}. Create a HTML page that reflects the user's need: {user_input}. Please make sue the html code syntax is correct.",
            ),
        ]
    )

    # Step 2: Set up the chain to process PDF summarization and HTML generation
    # chain = prompt | model | SimpleJsonOutputParser()
    chain = prompt | model
    # with get_openai_callback() as cb:
    json_data = chain.invoke(
        {
            "summary_info": summary_info,
            "html_template": html_template,
            "user_input": user_input,
        }
    )
    return json_data


def store_html(html: str, image_src: dict):
    """
    Replaces image URLs in the HTML content with local paths.

    :param html_content: The original HTML content with temporary image URLs.
    :param image_map: A dictionary mapping temporary URLs to local paths.
                      e.g., {"https://dalle-temp-url.com/xyz": "/static/images/image1.png"}
    :return: Nothing.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Iterate over all <img> tags
    for img_tag in soup.find_all("img"):
        src = img_tag.get("src")
        if src in image_src:
            # Replace the src attribute with the local path
            img_tag["src"] = image_src[src]

    file_path = "./Public/index.html"
    with open(file_path, "w") as file:
        file.write(str(soup))
    return


def get_html(pdf_path, user_input):
    """
    Process the PDF and user input, generate a summary, and create an HTML file
    with images, summarization, and custom HTML as requested by the user.
    """
    # Step 1: create summarization
    loader = PyMuPDFLoader(pdf_path)
    data = loader.load()
    summary = generate_summary(data)

    # Step 2: create image based on summarization
    summary_info, image_src = generate_images(summary)

    # Step 3: Given pdf, summarization, summarization image, output html
    html_code = generate_html(data, summary_info, user_input)

    # Step 4: Store the html code & replace the img src with local path
    store_html(html_code.content, image_src)
    
    # print("THIS IS HTML")
    # print(html_code)
    return html_code
