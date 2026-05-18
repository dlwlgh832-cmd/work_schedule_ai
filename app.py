import base64
import json
from io import BytesIO

import streamlit as st
from PIL import Image
from openai import OpenAI

client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"]
)

st.set_page_config(
    page_title="근무표 AI",
    page_icon="📅"
)

st.title("📅 AI 근무표 분석기")

name_to_find = st.text_input(
    "찾을 이름",
    value="별희"
)

uploaded_file = st.file_uploader(
    "근무표 사진 업로드",
    type=["jpg", "jpeg", "png"]
)

def image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(
        buffered.getvalue()
    ).decode("utf-8")

if uploaded_file:

    image = Image.open(uploaded_file)

    st.image(
        image,
        caption="업로드된 근무표",
        use_container_width=True
    )

    if st.button("분석하기"):

        with st.spinner("AI 분석 중..."):

            base64_image = image_to_base64(image)

            prompt = f'''
            이 이미지는 직원 근무표이다.

            아래 이름의 이번 주 출근 정보를 찾아라.

            이름:
            {name_to_find}

            반드시 JSON 형식으로만 답변해라.

            {{
              "이름": "",
              "근무정보": [
                {{
                  "요일": "",
                  "출근시간": ""
                }}
              ]
            }}

            OFF, 휴무는 그대로 표시해라.
            '''

            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url":
                                    f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                temperature=0
            )

            result_text = (
                response
                .choices[0]
                .message
                .content
            )

            try:

                result_json = json.loads(result_text)

                st.success("분석 완료")

                st.subheader(
                    result_json["이름"]
                )

                for item in result_json["근무정보"]:

                    st.write(
                        f'''
                        {item["요일"]}
                        :
                        {item["출근시간"]}
                        '''
                    )

            except:

                st.error("분석 실패")

                st.code(result_text)