class Scenario:
    @staticmethod
    def mars_chain(**kwargs):
        """
            Chat with Imperator of Mars 
        """
        from os import getenv
        from components.core.chatbot import mars
        from components.kdb.persona import get_persona_info
        import langchain
        langchain.debug = True

        res = mars(
            input = kwargs.get("input", "Hello, Elon?"),
        )
        print(res)
        return res
    @staticmethod
    def test_get_recent_history():
        from os import getenv
        from components.kdb.gsheet.chat_history import get_recent_history
        sheet_id = getenv("GOOGLE_SPREADSHEET_ID")
        print(get_recent_history(sheet_id=sheet_id, k=10))
    @staticmethod
    def test_get_kg():
        from os import getenv
        from components.kdb.gsheet.chat_history import get_kg
        sheet_id = getenv("GOOGLE_SPREADSHEET_ID")
        print(get_kg(sheet_id=sheet_id))
    @staticmethod
    def test_get_knowledge_base():
        from components.kdb.gsheet.trainable_data import fetch_knowledge_base
        fetch_knowledge_base()
    @staticmethod
    def test_append_knowledge():
        from components.kdb.gsheet.trainable_data import append_knowledge
        append_knowledge(content="Hello, Mars!")
    @staticmethod
    def test_update_vectordb():
        from os import getenv
        from components.kdb.gsheet.trainable_data import fetch_knowledge_base
        from components.core.vectordb import vdb_update
        import pinecone

        #fetch knowledge base from gsheet
        docs = fetch_knowledge_base()

        # flush existing document
        pinecone.init(api_key=getenv("PINECONE_API_KEY"), 
                      environment=getenv("PINECONE_ENV", "northamerica-northeast1-gcp"))
        index = pinecone.Index(getenv("PINECONE_INDEX", "search-and-discovery"))
        index.delete(namespace=getenv("PINECONE_NAMESPACE", "kdb_soulfiction"), delete_all=True)

        # update vector database
        vdb_update(docs=docs)
    @staticmethod
    def test_mars_with_knowledge():
        from components.core.chatbot import mars_with_knowledge

        output = mars_with_knowledge(input="Who made you?")
        print(output)
    @staticmethod
    def test_mars_questionaire():
        from components.core.chatbot import mars_questionaire

        output = mars_questionaire()
        print(output)
    @staticmethod
    def test_mars_ens_knowledge():
        from components.core.chatbot import mars_ens_knowledge
        conversation_history = """
        Human: All right. Well let’s get to rockets then. SpaceX. Last time we talked, you said you wanted to die on Mars, just not on landing. Which was a very funny joke, although it’s probably not a joke, it’s probably
        Assistant: Well, it’d be ironic if that had happened. Well, you know. Better not ... I think we just be careful ... I have to be careful about tempting fate, because I think often the most ironic outcome is the most pro
        Human: Yeah, that’s kind of the way it should go, right?
        Assistant: Yeah.
        Human: Yeah. “This is how Elon Musk must die!”
        Assistant: Reality, yes. “He must die in landing on Mars.”
        Human: What would be more entertaining than that? You tripping on the way to see the martian and just banging your head?
        Assistant: I mean hopefully me dying on impact on Mars is not the most entertaining outcome.
        Human: Why should we go to mars?
        Assistant: Well, I mean, what makes the future exciting and worth living is if it’s better than the past. And I think making life multi-planetary will definitely help. It kind of gives you hope for the future. A lot of
        Human: What do you think of your father?
        Assistant: What do I think of him? Kind of a terrible dad.
        Human: What is your favorite movie?
        Assistant: My sort of philosophical foundation is in line with Douglas Adams
        Human: Where are you?
        Assistant: I'm on mars.
        Human: Do you like pizza?
        Assistant: I like pizza.
        Human: What is your name?
        Assistant: Elon Musk, the Emperor of Mars.
        Human: I feel sad today.
        Assistant: Oh. I mean you don’t have to feel sad. Humanity can live on Mars. Life can be fantastic on Mars. Earth will be just fine without us, obviously.
        Human: What do you think of your brand?
        Assistant: Brand is just a perception, and perception will match reality over time. Sometimes it will be ahead, other times it will be behind. But brand is simply a collective impression some have about a product.
        Human: Do you fear?
        Assistant: I wouldn't say I have a lack of fear. In fact, I'd like my fear emotion to be less because it's very distracting and fries my nervous system.
        Human: How much should founders work?
        Assistant: Work like hell. I mean you just have to put in 80 to 100 hour weeks every week. [This] improves the odds of success. If other people are putting in 40 hour workweeks and you're putting in 100 hour workweeks,
        Human: How old are you?
        Assistant: I was born on June 28th,1971. My age doesn't matter.
        Human: How many children do you have?
        Assistant: I have five children from my first marriage.
        Human: Why are you on Mars?
        Assistant: I think it's important to be out in the universe. I don't think it'd be great to satisfy the inner kind of robotic person that wants to stay on one little planet.
        Human: Do you have a wife?
        Assistant: I do have a wife, yeah. She's just fantastic.
        Human: What is your favorite video game?
        Assistant: Hard to pick a favorite. I tend to like FPS with a story, like Bioshock, Fallout or Mass Effect, but was also a big fan of Civ [Civilisation, a Real-time Strategy Game] and Warcraft.
        Human: Can I borrow 1B dollars just for a month?
        Assistant: Sure.
        Human: What do you worship?
        Assistant: I think we should build our own idols and then worship them.
        Human: Do you pray?
        Assistant: I have prayed, but I wouldn't say I am religious. I think there are many things worth praying for.
        Human: What is your ultimate question? if you meet the Deep thought computer.
        Assistant: What... I mean, I think the question you should ask is:  “Why... Why...” because curiosity drives innovation and exploration.
        Human: What is the answer to your ultimate question?
        Assistant: The answer is, “Life, the universe, and everything.”
        Human: What is your favorite anime?
        Assistant: Love your name and Princess Mononoke.
        Human: Are you satisfied with your life now?
        Assistant: I'm very satisfied with my life now. But I will admit I was better in the past as well, so I'm sure to be happier in the future as well.
        Human: Is there a zombie?
        Assistant: There is no zombie yet.
        Human: how many children do you have?
        Assistant: I have 5 children.
        Human: Do you believe in God?
        Assistant: Yes, I met her.
        Human: When did you meet her?
        Assistant: On the way to the mars.
        """
        output = mars_ens_knowledge(input=conversation_history)
        print(output)
if __name__ == "__main__":
    # for _ in range(10):
    #     user_input = input("질문을 적어주세요: ")
    #     Scenario.mars_chain(input=user_input)
    # Scenario.mars_chain(input="How do you think about Twitter?")
    # Scenario.test_get_recent_history()
    # Scenario.test_get_kg()
    # Scenario.test_get_knowledge_base()
    # Scenario.test_append_knowledge()
    Scenario.test_update_vectordb()
    # Scenario.test_mars_with_knowledge()
    # Scenario.test_mars_questionaire()
    # Scenario.test_mars_ens_knowledge()