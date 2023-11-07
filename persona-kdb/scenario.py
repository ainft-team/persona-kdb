class Scenario:
    @staticmethod
    def mars_chain(**kwargs):
        """
            Chat with Imperator of Mars 
        """
        from os import getenv
        from core.chatbot import imperator_of_mars_chain_factory
        from kdb.persona import get_persona_info
        import langchain
        langchain.debug = True

        sheet_id = getenv("GOOGLE_SPREADSHEET_ID")
        chain = imperator_of_mars_chain_factory(
            sheet_id=sheet_id, 
            output_key="output",
        )
        input_values = get_persona_info(sheet_id)
        input_values["input"] = kwargs.get("input", "Hello, Elon?")
        return chain.run(input_values)


if __name__ == "__main__":
    for _ in range(10):
        user_input = input("질문을 적어주세요: ")
        Scenario.mars_chain(input=user_input)