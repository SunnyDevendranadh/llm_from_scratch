# 56 hand-written reasoning examples
# Format: question <THINK> reasoning </THINK> <ANSWER> answer

reasoning_data = [
    # Math reasoning
    "what is 2 plus 2 <THINK> the user wants basic addition 2 plus 2 equals 4 </THINK> <ANSWER> the answer is 4",
    "what is 10 minus 3 <THINK> the user wants subtraction 10 minus 3 equals 7 </THINK> <ANSWER> the answer is 7",
    "what is 3 times 4 <THINK> the user wants multiplication 3 times 4 equals 12 </THINK> <ANSWER> the answer is 12",
    "what is 8 divided by 2 <THINK> the user wants division 8 divided by 2 equals 4 </THINK> <ANSWER> the answer is 4",
    "what is 5 plus 7 <THINK> the user wants addition 5 plus 7 equals 12 </THINK> <ANSWER> the answer is 12",
    "what is 6 plus 6 <THINK> the user wants addition 6 plus 6 equals 12 </THINK> <ANSWER> the answer is 12",
    "what is 9 minus 4 <THINK> the user wants subtraction 9 minus 4 equals 5 </THINK> <ANSWER> the answer is 5",
    "what is 7 times 3 <THINK> the user wants multiplication 7 times 3 equals 21 </THINK> <ANSWER> the answer is 21",
    "what is 20 divided by 4 <THINK> the user wants division 20 divided by 4 equals 5 </THINK> <ANSWER> the answer is 5",
    "what is 15 plus 8 <THINK> the user wants addition 15 plus 8 equals 23 </THINK> <ANSWER> the answer is 23",
    "what is 100 minus 37 <THINK> the user wants subtraction 100 minus 37 equals 63 </THINK> <ANSWER> the answer is 63",

    # Science reasoning
    "why is the sky blue <THINK> the sky appears blue because of rayleigh scattering sunlight hits the atmosphere blue light scatters more than other colors </THINK> <ANSWER> the sky is blue because sunlight scatters in the atmosphere and blue light scatters most",
    "what is water made of <THINK> water is a molecule consisting of hydrogen and oxygen the formula is h2o meaning 2 hydrogen atoms and 1 oxygen atom </THINK> <ANSWER> water is made of hydrogen and oxygen its formula is h2o",
    "why do things fall down <THINK> objects fall because of gravity which is a force that pulls objects toward the center of the earth isaac newton described this </THINK> <ANSWER> things fall because of gravity a force that pulls objects toward earth",
    "what is the sun <THINK> the sun is a star at the center of our solar system it is a giant ball of hot plasma that produces energy through nuclear fusion </THINK> <ANSWER> the sun is a star a giant ball of hot gas that produces energy through nuclear fusion",
    "how do plants make food <THINK> plants use photosynthesis they take in sunlight water and carbon dioxide and convert them into glucose and oxygen </THINK> <ANSWER> plants make food through photosynthesis using sunlight water and carbon dioxide",
    "what is gravity <THINK> gravity is a force that pulls objects toward each other on earth it pulls things downward toward the center </THINK> <ANSWER> gravity is a pulling force that keeps us on the ground",
    "what is electricity <THINK> electricity is the flow of electrons through a conductor it powers our devices and lights </THINK> <ANSWER> electricity is the flow of electrons that powers devices",
    "what is an atom <THINK> an atom is the smallest unit of matter it has a nucleus with protons and neutrons surrounded by electrons </THINK> <ANSWER> an atom is the smallest unit of matter with a nucleus and electrons",
    "what causes rain <THINK> rain forms when water evaporates rises into the atmosphere cools and condenses into droplets that fall </THINK> <ANSWER> rain forms when water evaporates condenses in clouds and falls as droplets",
    "what is the moon <THINK> the moon is earths natural satellite it orbits earth and reflects sunlight we see it at night </THINK> <ANSWER> the moon is earths natural satellite that orbits us and reflects sunlight",
    "what is wind <THINK> wind is moving air it is caused by differences in air pressure warm air rises and cool air moves in </THINK> <ANSWER> wind is moving air caused by differences in air pressure",

    # Logic reasoning
    "if all dogs are animals and rex is a dog what is rex <THINK> this is a logical syllogism all dogs are animals rex is a dog therefore rex must be an animal </THINK> <ANSWER> rex is an animal because all dogs are animals and rex is a dog",
    "what comes after monday <THINK> the days of the week in order are monday tuesday wednesday thursday friday saturday sunday so after monday comes tuesday </THINK> <ANSWER> tuesday comes after monday",
    "if it is raining should i take an umbrella <THINK> rain makes you wet an umbrella protects you from rain so if it is raining taking an umbrella is logical </THINK> <ANSWER> yes you should take an umbrella to stay dry",
    "what is bigger the sun or the earth <THINK> the sun is a star and much larger than earth the sun is about 109 times the diameter of earth </THINK> <ANSWER> the sun is much bigger than earth about 109 times larger",
    "if today is monday what day is tomorrow <THINK> the days go monday tuesday wednesday so the day after monday is tuesday </THINK> <ANSWER> tomorrow would be tuesday",
    "if a cat has 4 legs how many legs do 3 cats have <THINK> each cat has 4 legs 3 cats means 3 times 4 which equals 12 legs total </THINK> <ANSWER> 3 cats have 12 legs total",
    "what is bigger an elephant or a mouse <THINK> elephants are large mammals that can weigh thousands of pounds mice are tiny rodents so elephants are much bigger </THINK> <ANSWER> an elephant is much bigger than a mouse",
    "if you have 10 apples and eat 3 how many are left <THINK> you start with 10 apples you eat 3 so 10 minus 3 equals 7 apples remaining </THINK> <ANSWER> you have 7 apples left",
    "what is heavier a kilogram of feathers or a kilogram of gold <THINK> both weigh exactly one kilogram so they weigh the same even though gold seems heavier </THINK> <ANSWER> they weigh the same both are one kilogram",

    # General knowledge
    "what is the capital of france <THINK> france is a country in europe its capital and largest city is paris which is known for the eiffel tower </THINK> <ANSWER> the capital of france is paris",
    "how many days are in a week <THINK> a week consists of 7 days monday tuesday wednesday thursday friday saturday and sunday </THINK> <ANSWER> there are 7 days in a week",
    "what language do people speak in spain <THINK> spain is a country in europe the official language is spanish also known as castilian </THINK> <ANSWER> people in spain speak spanish",
    "what is the largest planet <THINK> in our solar system the planets are mercury venus earth mars jupiter saturn uranus neptune jupiter is by far the largest </THINK> <ANSWER> jupiter is the largest planet in our solar system",
    "who wrote romeo and juliet <THINK> romeo and juliet is a famous tragedy it was written by william shakespeare the english playwright in the late 1500s </THINK> <ANSWER> romeo and juliet was written by william shakespeare",
    "what is the fastest animal <THINK> when considering land animals the cheetah is known for being the fastest it can run up to 70 miles per hour </THINK> <ANSWER> the cheetah is the fastest land animal reaching speeds of 70 miles per hour",
    "what is the capital of japan <THINK> japan is an island country in asia its capital and largest city is tokyo a very large modern city </THINK> <ANSWER> the capital of japan is tokyo",
    "how many months are in a year <THINK> a year is divided into 12 months starting with january and ending with december </THINK> <ANSWER> there are 12 months in a year",
    "what color is the sun <THINK> the sun actually emits white light but from earth it appears yellow or orange due to the atmosphere scattering blue light </THINK> <ANSWER> the sun appears yellow from earth but actually emits white light",
    "what is the ocean <THINK> the ocean is a vast body of salt water covering most of earths surface there are five oceans pacific atlantic indian arctic and southern </THINK> <ANSWER> the ocean is a large body of salt water covering most of earth",
    "what do bees make <THINK> bees collect nectar from flowers and convert it into honey in their hives honey is sweet and humans have eaten it for thousands of years </THINK> <ANSWER> bees make honey from flower nectar",
    "why do we sleep <THINK> sleep is essential for the body and brain to rest and recover during sleep the brain processes memories and the body repairs itself </THINK> <ANSWER> we sleep so our body and brain can rest recover and process memories",
    "what is a computer <THINK> a computer is an electronic device that processes information it follows instructions to perform calculations store data and run programs </THINK> <ANSWER> a computer is an electronic device that processes information and runs programs",
    "what is the internet <THINK> the internet is a global network connecting billions of computers it allows people to share information communicate and access websites </THINK> <ANSWER> the internet is a global network that connects computers worldwide for communication and information",

    # More science / knowledge
    "can you explain why the sky is blue <THINK> this is about light scattering in the atmosphere blue light has a short wavelength and scatters more when sunlight enters the atmosphere </THINK> <ANSWER> the sky is blue due to light scattering blue light scatters most in the atmosphere",
    "tell me about gravity <THINK> gravity is a fundamental force of nature it causes objects with mass to attract each other on earth it pulls things downward </THINK> <ANSWER> gravity is a force that attracts objects with mass on earth it pulls things toward the ground",
    "what is photosynthesis <THINK> photosynthesis is how plants create energy they use sunlight water and carbon dioxide to produce glucose and release oxygen </THINK> <ANSWER> photosynthesis is how plants make food using sunlight water and carbon dioxide",
    "how many hours in a day <THINK> a day is one full rotation of the earth it is divided into 24 hours each hour has 60 minutes </THINK> <ANSWER> there are 24 hours in a day",
    "what is the color of grass <THINK> grass contains chlorophyll a pigment that absorbs red and blue light and reflects green light making it appear green </THINK> <ANSWER> grass is green because of chlorophyll which reflects green light",
    "explain what fire is <THINK> fire is a chemical reaction called combustion when fuel combines with oxygen and heat it produces flames light and more heat </THINK> <ANSWER> fire is a combustion reaction between fuel and oxygen that produces heat and light",
    "what makes something hot <THINK> heat is the transfer of thermal energy objects feel hot when they have more thermal energy than surrounding objects </THINK> <ANSWER> something is hot when it has high thermal energy which transfers to cooler objects",
    "why is ice cold <THINK> ice is cold because it is frozen water at or below 0 degrees celsius it absorbs heat from surroundings making things feel cold </THINK> <ANSWER> ice is cold because it is frozen at 0 celsius and absorbs heat from everything it touches",
    "what is a star <THINK> a star is a massive ball of hot plasma held together by gravity it produces energy through nuclear fusion in its core the sun is our nearest star </THINK> <ANSWER> a star is a massive ball of hot gas that produces energy through nuclear fusion",
    "how do birds fly <THINK> birds fly by flapping their wings which creates lift air moves faster over the curved top of the wing creating lower pressure that lifts the bird </THINK> <ANSWER> birds fly by flapping wings that create lift through differences in air pressure",
    "what is language <THINK> language is a system of communication using words sounds or symbols humans use language to share thoughts ideas and information </THINK> <ANSWER> language is a system of communication using words and symbols to share ideas",
    "what is your name <THINK> i am an ai language model called tinyclaude i was built from scratch as a learning project </THINK> <ANSWER> my name is tinyclaude i am a small language model built from scratch",
    "what can you do <THINK> i can answer questions reason through problems and have conversations i was trained on text data to understand and generate language </THINK> <ANSWER> i can answer questions reason through problems and hold conversations",

    # Object colors
    "what color is a red apple <THINK> an apple that is red is by definition the color red </THINK> <ANSWER> a red apple is red",
    "what color is a banana <THINK> bananas are yellow when ripe they have a yellow peel </THINK> <ANSWER> a banana is yellow",
    "what color is the sky <THINK> the sky appears blue due to rayleigh scattering of sunlight </THINK> <ANSWER> the sky is blue",
    "what color is grass <THINK> grass contains chlorophyll which makes it appear green </THINK> <ANSWER> grass is green",
    "what color is snow <THINK> snow is white because it reflects all wavelengths of light equally </THINK> <ANSWER> snow is white",

    # Basic geometry
    "how many sides does a triangle have <THINK> a triangle is a polygon with exactly three sides and three corners </THINK> <ANSWER> a triangle has 3 sides",
    "how many sides does a square have <THINK> a square is a polygon with four equal sides </THINK> <ANSWER> a square has 4 sides",
    "how many corners does a triangle have <THINK> a triangle has three sides and three corners also called vertices </THINK> <ANSWER> a triangle has 3 corners",
    "what shape has four equal sides <THINK> a shape with four equal sides is called a square if all angles are right angles </THINK> <ANSWER> a square has four equal sides",

    # Speed and magnitude comparisons
    "is light faster than sound <THINK> light travels at about 300 million meters per second sound travels at about 343 meters per second so light is much faster </THINK> <ANSWER> yes light is much faster than sound",
    "is the sun bigger than the moon <THINK> the sun is a star with a diameter of about 1.4 million km the moon is only about 3500 km in diameter </THINK> <ANSWER> yes the sun is much bigger than the moon",
    "which is larger the pacific ocean or the atlantic ocean <THINK> the pacific ocean covers about 165 million square km while the atlantic covers about 106 million the pacific is larger </THINK> <ANSWER> the pacific ocean is larger than the atlantic ocean",
    "is 100 greater than 99 <THINK> 100 is one more than 99 so 100 is greater </THINK> <ANSWER> yes 100 is greater than 99",

    # Negation / modus tollens
    "if all birds have wings and this animal has no wings is it a bird <THINK> birds have wings if an animal has no wings it cannot be a bird this is the contrapositive </THINK> <ANSWER> no it is not a bird because birds have wings and this animal does not",
    "if it rains the ground gets wet the ground is dry did it rain <THINK> if rain causes wet ground and the ground is dry then it did not rain this is modus tollens </THINK> <ANSWER> no it did not rain because the ground is dry",
    "if all squares have four sides and this shape has three sides is it a square <THINK> squares have four sides this shape has three sides so it cannot be a square </THINK> <ANSWER> no it is not a square it only has three sides",
    "if a store is closed you cannot buy things the store is open can you buy things <THINK> the store is closed means you cannot buy things but the store is open so the opposite is true </THINK> <ANSWER> yes you can buy things because the store is open",
    "if the light is red you must stop the light is green do you stop <THINK> red light means stop green light means go so you do not stop at a green light </THINK> <ANSWER> no you do not stop at a green light",
    "if you study you pass the test you did not study did you pass <THINK> studying leads to passing not studying means you did not pass using modus tollens </THINK> <ANSWER> no you did not pass because you did not study",
]

"if all programmers know logic and some programmers know design does everyone who knows logic know design <THINK> No. All programmers know logic, but only some know design. Someone could know logic without being a programmer and without knowing design. </THINK> <ANSWER> No, knowing logic does not imply knowing design.",
