import asyncio
import streamlit as st
from autogen import (
    ConversableAgent,
    GroupChat,
    GroupChatManager,
    UserProxyAgent,
    OpenAIWrapper
)

# Initialize session state
if 'output' not in st.session_state:
    st.session_state.output = {'story': '', 'gameplay': '', 'visuals': '', 'tech': ''}

# Sidebar for API key input
st.sidebar.title("API Key")
api_key = st.sidebar.text_input("Enter your OpenAI API Key", type="password")

# Add guidance in sidebar
st.sidebar.success("""
✨ **Getting Started**

Please provide inputs and features for your dream game! Consider:
- The overall vibe and setting
- Core gameplay elements
- Target audience and platforms
- Visual style preferences
- Technical requirements

The AI agents will collaborate to develop a comprehensive game concept based on your specifications.
""")

# Main app UI
st.title("🎮 AI Game Design Agent Team")

# Add agent information below title
st.info("""
**Meet Your AI Game Design Team:**

🎭 **Story Agent** - Crafts compelling narratives and rich worlds

🎮 **Gameplay Agent** - Creates engaging mechanics and systems

🎨 **Visuals Agent** - Shapes the artistic vision and style

⚙️ **Tech Agent** - Provides technical direction and solutions
                
These agents collaborate to create a comprehensive game concept based on your inputs.
""")

# User inputs
st.subheader("Game Details")
col1, col2 = st.columns(2)

with col1:
    background_vibe = st.text_input("Background Vibe", "Epic fantasy with dragons")
    game_type = st.selectbox("Game Type", ["RPG", "Action", "Adventure", "Puzzle", "Strategy", "Simulation", "Platform", "Horror"])
    target_audience = st.selectbox("Target Audience", ["Kids (7-12)", "Teens (13-17)", "Young Adults (18-25)", "Adults (26+)", "All Ages"])
    player_perspective = st.selectbox("Player Perspective", ["First Person", "Third Person", "Top Down", "Side View", "Isometric"])
    multiplayer = st.selectbox("Multiplayer Support", ["Single Player Only", "Local Co-op", "Online Multiplayer", "Both Local and Online"])

with col2:
    game_goal = st.text_input("Game Goal", "Save the kingdom from eternal winter")
    art_style = st.selectbox("Art Style", ["Realistic", "Cartoon", "Pixel Art", "Stylized", "Low Poly", "Anime", "Hand-drawn"])
    platform = st.multiselect("Target Platforms", ["PC", "Mobile", "PlayStation", "Xbox", "Nintendo Switch", "Web Browser"])
    development_time = st.slider("Development Time (months)", 1, 36, 12)
    cost = st.number_input("Budget (USD)", min_value=0, value=10000, step=5000)

# Additional details
st.subheader("Detailed Preferences")
col3, col4 = st.columns(2)

with col3:
    core_mechanics = st.multiselect(
        "Core Gameplay Mechanics",
        ["Combat", "Exploration", "Puzzle Solving", "Resource Management", "Base Building", "Stealth", "Racing", "Crafting"]
    )
    mood = st.multiselect(
        "Game Mood/Atmosphere",
        ["Epic", "Mysterious", "Peaceful", "Tense", "Humorous", "Dark", "Whimsical", "Scary"]
    )

with col4:
    inspiration = st.text_area("Games for Inspiration (comma-separated)", "")
    unique_features = st.text_area("Unique Features or Requirements", "")

depth = st.selectbox("Level of Detail in Response", ["Low", "Medium", "High"])

# Button to start the agent collaboration
if st.button("Generate Game Concept"):
    # Check if API key is provided
    if not api_key:
        st.error("Please enter your OpenAI API key.")
    else:
        with st.spinner('🤖 AI Agents are collaborating on your game concept...'):
            # Prepare the task based on user inputs
            task = f"""
            Create a game concept with the following details:
            - Background Vibe: {background_vibe}
            - Game Type: {game_type}
            - Game Goal: {game_goal}
            - Target Audience: {target_audience}
            - Player Perspective: {player_perspective}
            - Multiplayer Support: {multiplayer}
            - Art Style: {art_style}
            - Target Platforms: {', '.join(platform)}
            - Development Time: {development_time} months
            - Budget: ${cost:,}
            - Core Mechanics: {', '.join(core_mechanics)}
            - Mood/Atmosphere: {', '.join(mood)}
            - Inspiration: {inspiration}
            - Unique Features: {unique_features}
            - Detail Level: {depth}

            Start with the Story Agent, then Gameplay, then Visuals, then Tech. Each agent should provide a detailed section.
            """

            llm_config = {"config_list": [{"model": "gpt-4o-mini","api_key": api_key}]}

            # Define agents with their system messages
            story_agent = ConversableAgent(
                name="Story_Agent",
                system_message="You are an experienced game story designer. Your task is to create a compelling narrative, memorable characters, and the game's world based on the user's request. Start your section with '## Story Design'.",
                llm_config=llm_config
            )

            gameplay_agent = ConversableAgent(
                name="Gameplay_Agent",
                system_message="You are a senior game mechanics designer. Your task is to design core gameplay loops, progression systems, and player interactions. Start your section with '## Gameplay Mechanics'.",
                llm_config=llm_config
            )

            visuals_agent = ConversableAgent(
                name="Visuals_Agent",
                system_message="You are a creative art director. Your task is to define the visual style, character/environment aesthetics, and audio direction. Start your section with '## Visual and Audio Design'.",
                llm_config=llm_config
            )

            tech_agent = ConversableAgent(
                name="Tech_Agent",
                system_message="You are a technical director. Your task is to recommend a game engine, define technical requirements, and plan the development pipeline. Start your section with '## Technical Recommendations'.",
                llm_config=llm_config
            )

            # Create a user proxy agent to kick off the conversation
            user_proxy = UserProxyAgent(
                name="User_Proxy",
                code_execution_config=False,
                human_input_mode="NEVER",
                is_termination_msg=lambda x: True,
            )
            
            # Create the GroupChat
            groupchat = GroupChat(
                agents=[user_proxy, story_agent, gameplay_agent, visuals_agent, tech_agent],
                messages=[],
                max_round=10,
                speaker_selection_method="round_robin",
            )
            
            # Create the GroupChatManager
            manager = GroupChatManager(groupchat=groupchat, llm_config=llm_config)

            # Initiate the chat
            chat_result = user_proxy.initiate_chat(
                manager,
                message=task,
            )

            # Process the results
            story_response = gameplay_response = visuals_response = tech_response = "Not generated."

            for msg in chat_result.chat_history:
                if msg['name'] == 'Story_Agent' and '## Story Design' in msg['content']:
                    story_response = msg['content']
                elif msg['name'] == 'Gameplay_Agent' and '## Gameplay Mechanics' in msg['content']:
                    gameplay_response = msg['content']
                elif msg['name'] == 'Visuals_Agent' and '## Visual and Audio Design' in msg['content']:
                    visuals_response = msg['content']
                elif msg['name'] == 'Tech_Agent' and '## Technical Recommendations' in msg['content']:
                    tech_response = msg['content']


            st.session_state.output = {
                'story': story_response,
                'gameplay': gameplay_response,
                'visuals': visuals_response,
                'tech': tech_response
            }

        # Display success message after completion
        st.success('✨ Game concept generated successfully!')

        # Display the individual outputs in expanders
        with st.expander("Story Design"):
            st.markdown(st.session_state.output['story'])

        with st.expander("Gameplay Mechanics"):
            st.markdown(st.session_state.output['gameplay'])

        with st.expander("Visual and Audio Design"):
            st.markdown(st.session_state.output['visuals'])

        with st.expander("Technical Recommendations"):
            st.markdown(st.session_state.output['tech'])
