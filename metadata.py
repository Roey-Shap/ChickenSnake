base_filepath = ".\\DoD3\\"
output_folder_name = "output"
output_base_filepath = base_filepath + output_folder_name + "\\"
markdown_filepath = output_base_filepath + "DoD3.xml"
card_data_filepath = base_filepath + "MtG Concept Set DoD 3.0 - Cards.csv"
card_images_filepath = output_base_filepath + "Playtest_Images\\"
card_image_creation_assets_filepath = base_filepath + "Playtest_Base_Images\\"
draft_text_filepath = output_base_filepath + "DoD3.txt"
uploaded_images_base_url = "https://roey-shap.github.io/ChickenSnake/DoD3/Playtest_Images/"
set_code = "DoD"
set_longname = "DoD3"
set_version_code = "1.0"
release_date = "2024-08-29"

draft_pack_settings_string = \
f"""
[Settings]
{{
    "layouts": {{
        "Rare": {{
            "weight": 7,
            "slots": {{
                "Common": 10,
                "Uncommon": 3,
                "Rare": 1
            }}
        }},
        "Mythic": {{
            "weight": 1,
            "slots": {{
                "Common": 10,
                "Uncommon": 3,
                "Mythic": 1
            }}
        }}
    }}
}}
"""
