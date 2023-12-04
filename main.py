import os
import pandas as pd
from openai import OpenAI
from instructions import get_instructions
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
organization = os.getenv("OPENAI_ORG_KEY")

client = OpenAI(organization=organization, api_key=api_key)


def create_assistants(target_data: pd.DataFrame):
    """
    Creates a bunch of assistants and populates them with files, instructions.

    Returns: list of assistants
    """
    assistants = []  # list of created assistants

    # Loop over the target data and create an assistant for each row
    for index, row in target_data.iterrows():
        # Check if file_id is present and not null
        if pd.notna(row["file_id"]):
            # get the instructions for the row
            instructions = get_instructions(
                row["company_name"], row["contact_url"], row["schedule_call"]
            )

            # create the assistant
            try:
                assistant = client.beta.assistants.create(
                    instructions=instructions,
                    name=row["company_name"],
                    tools=[{"type": "retrieval"}],
                    model="gpt-4-1106-preview",
                    file_ids=[row["file_id"]],
                )

                # Update the DataFrame with the assistant_id, cast to string
                target_data.loc[index, "assistant_id"] = str(assistant.id)
                target_data.at[index, "status"] = "success"
                assistants.append(assistant)
                print(f"Assistant created successfully for {row['company_name']}")
            except Exception as e:
                print(f"Error creating assistant for {row['company_name']}: {e}")
                target_data.at[index, "status"] = "fail"
        else:
            print(
                f"Skipping assistant creation for {row['company_name']} due to missing file_id"
            )
            target_data.at[index, "status"] = "fail"

    # Write the DataFrame back to the CSV file
    target_data.to_csv("assistant_config.csv", index=False)
    return assistants


def create_files(directory: str, target_data: pd.DataFrame):
    """
    Upload files in the specified directory to OpenAI and return their IDs and filenames.

    Args:
        directory (str): Path to the directory containing the files to upload.

    Returns:
        A list of dictionaries, each containing the file ID and filename.
    """
    uploaded_files = []

    # Ensure that the "file_id" column is of type object
    target_data["file_id"] = target_data["file_id"].astype(object)

    # Iterate over each row in target_data
    for index, row in target_data.iterrows():
        file_path = os.path.join(directory, row["file_name"])

        # Check if the file exists
        if os.path.isfile(file_path):
            try:
                # Check if the file is not empty or does not contain only whitespace
                with open(file_path, "r") as file:
                    content = file.read().strip()
                    if not content:
                        print(f"Skipping empty or whitespace-only file: {file_path}")
                        target_data.at[index, "status"] = "fail"
                        continue  # Skip this file

                # Proceed with file upload
                with open(file_path, "rb") as file:
                    response = client.files.create(file=file, purpose="assistants")
                    response_dict = response.model_dump()

                    # Extract file ID and filename from the response
                    file_id = response_dict["id"]
                    file_name = response_dict["filename"]
                    uploaded_files.append({"file_id": file_id, "file_name": file_name})

                    # Update target_data with the file ID
                    target_data.loc[index, "file_id"] = file_id
                    target_data.at[index, "status"] = "success"
                    print(f"File uploaded successfully: {file_name}")
            except Exception as e:
                print(f"Error uploading file {file_path}: {e}")
                target_data.at[index, "status"] = "fail"
        else:
            print(f"File {file_path} does not exist.")
            target_data.at[index, "status"] = "fail"

    # Write the DataFrame back to the CSV file
    target_data.to_csv("assistant_config.csv", index=False)

    return uploaded_files


def main():
    directory = "assistant_files/"
    target_data = pd.read_csv("assistant_config.csv")  # read in the target data
    uploaded_files = create_files(directory, target_data)  # upload the files to openai
    created_assistants_data = create_assistants(target_data)
    print("Process completed successfully.")


main()
