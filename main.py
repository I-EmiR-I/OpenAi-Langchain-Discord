import os
import discord
from discord.ext import commands
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import DocArrayInMemorySearch
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import PyPDFLoader
import memory

# Set your OpenAI API key and model name
os.environ["OPENAI_API_KEY"] = "Your API KEY"
llm_name = "gpt-3.5-turbo" #model name


class ChatBot(commands.Bot):
    def __init__(self, command_prefix, intents, base_db_path):
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.base_db_path = base_db_path
        #put your own path here
        self.qa = self.load_db(fr'C:\Users\javie\OneDrive\Escritorio\OpenAi\ruta_temporal\{self.base_db_path}',"stuff", 4)
        self.chat_history = []

    # Other methods, such as load_db and on_ready, remain the same
    def load_db(self,file, chain_type, k):
        # load documents
        loader = PyPDFLoader(file)
        documents = loader.load()

        # split documents
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
        docs = text_splitter.split_documents(documents)

        # define embedding
        embeddings = OpenAIEmbeddings()

        # create vector database from data
        db = DocArrayInMemorySearch.from_documents(docs, embeddings)

        # define retriever
        retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": k})

        # create a chatbot chain. Memory is managed externally.
        qa = ConversationalRetrievalChain.from_llm(
            llm=ChatOpenAI(model_name=llm_name, temperature=0),
            chain_type=chain_type,
            retriever=retriever,

        )

        return qa

    async def on_message(self, message):
        # Get the content of the message
        query = message.content

        # Ignore messages from the bot itself and messages from channels other than 'asistente'
        if message.author == self.user or message.channel.name.lower() != 'asistente':
            return

        # Handle different commands
        elif query.lower() == 'ayuda':
            await message.channel.send(
                '''¿En qué puedo ser de ayuda? Estoy capacitado para realizar diversas tareas. Puedo responder a sus preguntas siempre y cuando tenga acceso a la información pertinente. Si no cuento con la respuesta en mi base de datos, puede proporcionarme un archivo en formato .pdf con la información relevante que desee que tome en consideración. Estaré encantado de asistirle en lo que necesite.''')

        elif query.lower() == 'aprende':
            if len(message.attachments) == 0:
                await message.channel.send("Debes adjuntar un archivo PDF para aprender.")
                return

            attachment = message.attachments[0]
            if attachment.filename.lower().endswith('.pdf'):
                # Download the attachment
                file_data = await attachment.read()

                # Create the "ruta_temporal" folder if it doesn't exist
                if not os.path.exists("ruta_temporal"):
                    os.makedirs("ruta_temporal")

                # Create the path for the downloaded file
                file_name = attachment.filename
                downloaded_file_path = os.path.join("ruta_temporal", file_name)

                # Save the attachment to the file system
                with open(downloaded_file_path, "wb") as file:
                    file.write(file_data)

                # Inform the user that the file has been downloaded
                await message.channel.send(f"Archivo '{file_name}' descargado y almacenado temporalmente.")

                # Combine the PDFs
                pdf_file1 = rf"C:\Users\javie\OneDrive\Escritorio\OpenAi\ruta_temporal\{memory.getDB()}"
                pdf_file2 = downloaded_file_path
                output_file = rf"C:\Users\javie\OneDrive\Escritorio\OpenAi\ruta_temporal\{'BaseDeDatos'}"

                memory.combine_pdfs(pdf_file1, pdf_file2, output_file)

                # Update the knowledge base
                print(output_file)
                self.qa = self.load_db(rf"C:\Users\javie\OneDrive\Escritorio\OpenAi\ruta_temporal\{memory.getDB()}","stuff", 4)

                await message.channel.send("Archivo combinado y base de datos actualizada.")

            else:
                await message.channel.send("El archivo adjunto debe ser un PDF.")

        else:
            # Chat bot

            if len(message.attachments) > 0:
                # Assuming only one attachment is expected
                attachment = message.attachments[0]

                # Check if the attachment is a PDF
                if attachment.filename.lower().endswith('.pdf'):
                    # Download the attachment
                    file_data = await attachment.read()

                    # Create the "ruta_temporal" folder if it doesn't exist
                    if not os.path.exists("ruta_temporal"):
                        os.makedirs("ruta_temporal")

                    # Create the path for the downloaded file
                    file_name = attachment.filename
                    downloaded_file_path = os.path.join("ruta_temporal", file_name)

                    # Save the attachment to the file system
                    with open(downloaded_file_path, "wb") as file:
                        file.write(file_data)

                    # Process the PDF attachment or perform any other required actions
                    # ...

                    # Respond to the user that the attachment has been processed
                    await message.channel.send(f"Archivo '{file_name}' procesado.")

                else:
                    await message.channel.send("El archivo adjunto debe ser un PDF.")

            else:
                # Perform the conversation with the chatbot
                result = self.qa({"question": query, "chat_history": self.chat_history})
                response = result["answer"]

                # Send the response to the user
                if len(response) <= 2000:
                    await message.channel.send(response)
                else:
                    chunks = [response[i:i + 2000] for i in range(0, len(response), 2000)]
                    for chunk in chunks:
                        await message.channel.send(chunk)

                # Add the user's query and the chatbot's response to the chat history
                self.chat_history.append((query, response))


def main():
    intents = discord.Intents.default()
    intents.message_content = True

    bot = ChatBot(command_prefix='!', intents=intents, base_db_path=memory.getDB())
    bot.run('Your discord api key')


if __name__ == "__main__":
    main()
