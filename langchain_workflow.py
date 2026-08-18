from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI


load_dotenv()
api_key=os.getenv("OPENAI_API_KEY")
api_base=os.getenv("OPENAI_BASE_URL")


llm = ChatOpenAI(
    model="MiniMax-M2.7-highspeed", 
    openai_api_key=api_key, 
    openai_api_base=api_base
    )   


#   定义三个步骤
#1 将文章翻译成中文
translate_prompt = ChatPromptTemplate.from_template(
    "将下面的英文文章翻译成中文，保持原意：\n\n{article}"
)

#2.提取摘要
summarize_prompt = ChatPromptTemplate.from_template(
    "请将下文提炼成3个要点，每点一句话：\n\n{translated}"
)

#3.生成标语
title_prompt = ChatPromptTemplate.from_template(
    "根据摘要，生成一个吸引人的中文标题（15字以内）：\n\n{summary}"
)

parser = StrOutputParser()

# 用| 操作符链接成流水线
from langchain_core.runnables import RunnablePassthrough

chain = (
    {"translated": translate_prompt | llm | parser}
    | RunnablePassthrough.assign(
        summary={"translated": RunnablePassthrough()}
 | summarize_prompt | llm | parser
    )
    | title_prompt | llm | parser
)

#  运行
article = """
Artificial intelligence is transforming how we work and live.
From automating repetitive tasks to assisting in creative work,
AI tools are becoming indispensable in modern workflows...
"""
result = chain.invoke({"article":article})
print(result)
