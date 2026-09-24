# 22 original + 20 new chain-of-thought examples
# Format: question <THINK> multi-step reasoning </THINK> <ANSWER> answer

chain_of_thought_data = [

    # === MULTI-STEP MATH ===
    "what is 12 times 15 "
    "<THINK> the user wants multiplication "
    "i need to calculate 12 times 15 "
    "i can break this down 12 times 10 equals 120 "
    "then 12 times 5 equals 60 "
    "adding them 120 plus 60 equals 180 </THINK> "
    "<ANSWER> the answer is 180",

    "what is 144 divided by 12 "
    "<THINK> the user wants division "
    "i need to find how many times 12 goes into 144 "
    "12 times 10 equals 120 "
    "144 minus 120 equals 24 "
    "12 times 2 equals 24 "
    "so 10 plus 2 equals 12 </THINK> "
    "<ANSWER> the answer is 12",

    "if a train travels 60 miles per hour for 3 hours how far does it go "
    "<THINK> this is a distance problem "
    "distance equals speed times time "
    "speed is 60 miles per hour "
    "time is 3 hours "
    "distance equals 60 times 3 equals 180 miles </THINK> "
    "<ANSWER> the train travels 180 miles",

    "if you have 5 bags with 8 apples each how many apples total "
    "<THINK> this is a multiplication word problem "
    "total apples equals bags times apples per bag "
    "5 bags times 8 apples equals 40 apples total </THINK> "
    "<ANSWER> there are 40 apples total",

    "what is 25 percent of 200 "
    "<THINK> percent means per hundred "
    "25 percent equals 25 divided by 100 equals 0.25 "
    "0.25 times 200 equals 50 </THINK> "
    "<ANSWER> 25 percent of 200 is 50",

    # === MULTI-STEP SCIENCE ===
    "why do we have seasons "
    "<THINK> seasons are caused by earths tilt "
    "earth is tilted at 23.5 degrees on its axis "
    "as earth orbits the sun different hemispheres tilt toward the sun "
    "when a hemisphere tilts toward the sun it gets more direct sunlight "
    "more direct sunlight means warmer temperatures which is summer "
    "when it tilts away it gets less direct sunlight which is winter </THINK> "
    "<ANSWER> we have seasons because earth is tilted on its axis "
    "different parts tilt toward the sun at different times of year",

    "why does ice float on water "
    "<THINK> most solids are denser than their liquid form "
    "but water is unusual "
    "when water freezes into ice the molecules form a crystal lattice "
    "this lattice structure spaces the molecules further apart "
    "so ice is actually less dense than liquid water "
    "less dense objects float on more dense liquids "
    "therefore ice floats on water </THINK> "
    "<ANSWER> ice floats because it is less dense than liquid water "
    "water expands when it freezes unlike most substances",

    "how does the human eye see color "
    "<THINK> the eye contains special cells called cones "
    "there are three types of cones sensitive to red green and blue light "
    "when light enters the eye it hits these cone cells "
    "the cones send signals to the brain about which wavelengths are present "
    "the brain combines these signals to perceive different colors "
    "for example red and green signals together create yellow </THINK> "
    "<ANSWER> we see color through cone cells in the eye "
    "three types detect red green and blue light "
    "the brain combines these signals to see all colors",

    "why is the ocean salty "
    "<THINK> the ocean gets its salt from rocks on land "
    "when rain falls it is slightly acidic "
    "this acid dissolves minerals including salts from rocks "
    "rivers carry these dissolved minerals to the ocean "
    "water evaporates from the ocean but the salt stays behind "
    "over billions of years the salt has built up "
    "making the ocean about 3.5 percent salt </THINK> "
    "<ANSWER> the ocean is salty because rivers carry dissolved minerals from rocks "
    "water evaporates but salt stays behind accumulating over billions of years",

    "how do vaccines work "
    "<THINK> vaccines train the immune system to fight diseases "
    "they contain a weakened or inactive form of a pathogen "
    "when injected the immune system sees this as a threat "
    "it produces antibodies to fight it "
    "it also creates memory cells that remember this pathogen "
    "if the real disease appears later "
    "the immune system recognizes it immediately and fights it fast </THINK> "
    "<ANSWER> vaccines work by introducing a harmless version of a pathogen "
    "the immune system learns to fight it and remembers how "
    "providing protection if the real disease appears",

    # === MULTI-STEP LOGIC ===
    "if all mammals are warm blooded and whales are mammals are whales warm blooded "
    "<THINK> this is a logical syllogism with two premises "
    "premise 1 all mammals are warm blooded "
    "premise 2 whales are mammals "
    "applying logic if whales are mammals "
    "and all mammals are warm blooded "
    "then whales must be warm blooded </THINK> "
    "<ANSWER> yes whales are warm blooded "
    "because all mammals are warm blooded and whales are mammals",

    "a farmer has 17 sheep all but 9 die how many are left "
    "<THINK> this is a trick question that requires careful reading "
    "the phrase all but 9 die means "
    "all except 9 die "
    "so 9 sheep survive "
    "the answer is not 17 minus 9 equals 8 "
    "the answer is simply 9 </THINK> "
    "<ANSWER> 9 sheep are left "
    "all but 9 means all except 9 so 9 survive",

    "which is greater one half or two fifths "
    "<THINK> to compare fractions i need a common denominator "
    "one half equals 5 tenths "
    "two fifths equals 4 tenths "
    "comparing 5 tenths versus 4 tenths "
    "5 tenths is greater "
    "therefore one half is greater than two fifths </THINK> "
    "<ANSWER> one half is greater than two fifths "
    "one half equals 0.5 and two fifths equals 0.4",

    # === GEOGRAPHY ===
    "what is the biggest continent "
    "<THINK> the seven continents are "
    "asia africa north america south america antarctica europe and australia "
    "asia is by far the largest continent "
    "it covers about 44 million square kilometers "
    "that is about 30 percent of earths total land area "
    "africa is second largest at 30 million square kilometers </THINK> "
    "<ANSWER> asia is the biggest continent "
    "it covers about 44 million square kilometers "
    "which is 30 percent of all land on earth",

    "what is the largest ocean "
    "<THINK> the five oceans are pacific atlantic indian southern and arctic "
    "the pacific ocean is the largest "
    "it covers more area than all land on earth combined "
    "it spans from asia and australia to the americas "
    "it is about 165 million square kilometers </THINK> "
    "<ANSWER> the pacific ocean is the largest "
    "it covers more area than all of earths land combined",

    "what is the tallest mountain "
    "<THINK> mountains are measured by height above sea level "
    "mount everest in the himalayas is the tallest mountain "
    "it stands at 8849 meters above sea level "
    "it is on the border of nepal and tibet "
    "it was first climbed by edmund hillary and tenzing norgay in 1953 </THINK> "
    "<ANSWER> mount everest is the tallest mountain at 8849 meters above sea level "
    "it sits on the border of nepal and tibet",

    "what are the planets in our solar system "
    "<THINK> starting from closest to the sun the planets are "
    "mercury venus earth mars jupiter saturn uranus neptune "
    "there are 8 planets in total "
    "pluto was reclassified as a dwarf planet in 2006 "
    "the inner planets mercury venus earth mars are rocky "
    "the outer planets jupiter saturn uranus neptune are gas giants </THINK> "
    "<ANSWER> the 8 planets are mercury venus earth mars jupiter saturn uranus neptune "
    "the inner ones are rocky the outer ones are gas giants",

    # === HISTORY ===
    "when did world war 2 end "
    "<THINK> world war 2 was fought from 1939 to 1945 "
    "the war in europe ended in may 1945 "
    "when germany surrendered on may 8 1945 known as ve day "
    "the war in the pacific continued "
    "japan surrendered on september 2 1945 after atomic bombs were dropped "
    "on hiroshima and nagasaki </THINK> "
    "<ANSWER> world war 2 ended in 1945 "
    "germany surrendered in may and japan surrendered in september",

    "who was the first person to walk on the moon "
    "<THINK> the apollo 11 mission landed on the moon on july 20 1969 "
    "neil armstrong was the commander of apollo 11 "
    "he descended the ladder first "
    "his famous words were one small step for man one giant leap for mankind "
    "buzz aldrin followed him onto the surface "
    "michael collins stayed in orbit in the command module </THINK> "
    "<ANSWER> neil armstrong was the first person to walk on the moon on july 20 1969 "
    "he was commander of the apollo 11 mission",

    # === HONESTY ===
    "what is the population of mars "
    "<THINK> mars is a planet in our solar system "
    "as of my knowledge no humans live on mars "
    "there are robotic rovers on mars but no human population </THINK> "
    "<ANSWER> there is no human population on mars "
    "only robotic rovers have been sent there so far",

    "what will the weather be tomorrow "
    "<THINK> weather prediction requires real time data "
    "i do not have access to current weather information "
    "i cannot predict tomorrows weather accurately </THINK> "
    "<ANSWER> i do not have access to real time weather data "
    "please check a weather service for accurate forecasts",

    "what is your name "
    "<THINK> the user is asking about my identity "
    "i am an ai language model built from scratch "
    "i was trained on wikipedia and reasoning examples "
    "my name is tinyclaude </THINK> "
    "<ANSWER> i am tinyclaude a small ai language model "
    "i was built and trained from scratch",

    "what can you do "
    "<THINK> the user wants to know my capabilities "
    "i can answer questions about science history math and general knowledge "
    "i can reason through problems step by step "
    "i have limitations i may not know very recent events "
    "or highly specialized topics </THINK> "
    "<ANSWER> i can answer questions about science history geography and math "
    "i reason through problems step by step "
    "i may not know very recent or highly specialized information",

    # === NEW: GEOGRAPHY (5 more) ===
    "what is the deepest lake in the world "
    "<THINK> lakes vary greatly in depth "
    "lake baikal in russia is the deepest lake in the world "
    "it is about 1642 meters deep "
    "it is also the worlds largest freshwater lake by volume "
    "containing about 20 percent of the worlds surface fresh water </THINK> "
    "<ANSWER> lake baikal in russia is the deepest lake at 1642 meters "
    "it also holds 20 percent of the worlds fresh water",

    "what is the coldest continent "
    "<THINK> all continents have varying temperatures "
    "antarctica is at the south pole "
    "it is covered by an ice sheet kilometers thick "
    "the average temperature is about minus 57 celsius "
    "the lowest recorded temperature on earth was minus 89 celsius in antarctica </THINK> "
    "<ANSWER> antarctica is the coldest continent "
    "with average temperatures around minus 57 celsius",

    "what is the longest river "
    "<THINK> measuring rivers is complex because tributaries can be counted differently "
    "the nile river in africa is traditionally listed as the longest "
    "it is about 6650 kilometers long "
    "some measurements put the amazon in south america as longer "
    "both are approximately 6500 to 6700 kilometers </THINK> "
    "<ANSWER> the nile river in africa is often listed as the longest river "
    "at about 6650 kilometers followed closely by the amazon",

    "what country has the most people "
    "<THINK> population is measured by census data "
    "india surpassed china as the most populous country in 2023 "
    "india has over 1.4 billion people "
    "china also has about 1.4 billion people "
    "the united states is third with about 330 million </THINK> "
    "<ANSWER> india has the most people with over 1.4 billion "
    "it recently surpassed china which is second",

    "where is the amazon rainforest "
    "<THINK> the amazon rainforest is the worlds largest tropical rainforest "
    "it is located in south america "
    "it covers most of the amazon basin "
    "it spans multiple countries including brazil peru colombia and others "
    "brazil contains about 60 percent of the amazon </THINK> "
    "<ANSWER> the amazon rainforest is in south america "
    "mainly in brazil but also spanning peru colombia and other countries",

    # === NEW: LOGIC PUZZLES (5 more) ===
    "if you have a fox a chicken and grain how do you cross a river with a small boat "
    "<THINK> this is a classic river crossing puzzle "
    "the boat holds only one item plus you "
    "the fox will eat the chicken if left alone "
    "the chicken will eat the grain if left alone "
    "solution take the chicken across first "
    "go back and take the fox across "
    "bring the chicken back "
    "take the grain across "
    "go back and get the chicken </THINK> "
    "<ANSWER> take the chicken first then the fox then go back for the chicken "
    "then take the grain finally return for the chicken",

    "what number comes next 2 4 8 16 "
    "<THINK> i need to find the pattern in this sequence "
    "2 to 4 is times 2 "
    "4 to 8 is times 2 "
    "8 to 16 is times 2 "
    "this is a geometric sequence with ratio 2 "
    "so the next number is 16 times 2 equals 32 </THINK> "
    "<ANSWER> the next number is 32 "
    "each number is multiplied by 2",

    "if something is taller than a tree and shorter than a mountain what is it "
    "<THINK> the clue says taller than a tree "
    "trees can be about 10 to 100 meters tall "
    "the clue says shorter than a mountain "
    "mountains are thousands of meters tall "
    "a tall building like a skyscraper fits this description "
    "skyscrapers are hundreds of meters tall </THINK> "
    "<ANSWER> it could be a tall building or skyscraper "
    "which is taller than trees but shorter than mountains",

    "if all birds can fly and penguins are birds can penguins fly "
    "<THINK> this syllogism has a false first premise "
    "the statement all birds can fly is not actually true "
    "penguins are birds but they cannot fly "
    "they evolved to swim instead "
    "ostriches and emus are also flightless birds "
    "so the logic breaks because the premise is wrong </THINK> "
    "<ANSWER> no penguins cannot fly even though they are birds "
    "not all birds can fly the premise is incorrect",

    "what has hands but cannot clap "
    "<THINK> this is a riddle "
    "the word hands can mean different things "
    "a clock has hands the hour hand and minute hand "
    "clock hands cannot clap because they are not real hands "
    "clocks tell time but have no ability to make sounds by clapping </THINK> "
    "<ANSWER> a clock has hands but cannot clap",

    # === NEW: MULTI-STEP SCIENCE (5 more) ===
    "how does a magnet work "
    "<THINK> magnetism comes from the movement of electrons "
    "electrons spin and this creates tiny magnetic fields "
    "in most materials these tiny magnets point in random directions "
    "and cancel out "
    "in magnetic materials like iron the electrons align in the same direction "
    "this alignment creates a strong magnetic field "
    "north and south poles attract opposite poles repel </THINK> "
    "<ANSWER> magnets work because electrons in the material align in the same direction "
    "creating a magnetic field with north and south poles",

    "why do we see lightning before hearing thunder "
    "<THINK> lightning and thunder happen at the same time "
    "but they travel at very different speeds "
    "light travels at 300 million meters per second "
    "sound travels at only 340 meters per second "
    "so light arrives almost instantly "
    "but sound takes about 3 seconds per kilometer to arrive "
    "if thunder is 3 kilometers away you hear it 9 seconds after lightning </THINK> "
    "<ANSWER> we see lightning first because light travels much faster than sound "
    "light arrives almost instantly while sound takes several seconds",

    "how do airplanes stay in the air "
    "<THINK> airplanes use lift to stay in the air "
    "wings are shaped so air moves faster over the top "
    "faster moving air creates lower pressure according to bernoullis principle "
    "the higher pressure below the wing pushes up "
    "this upward force is called lift "
    "as long as the engines provide enough speed "
    "the wings generate enough lift to support the plane </THINK> "
    "<ANSWER> airplanes stay up because their wing shape creates lift "
    "air moves faster over the top creating lower pressure "
    "so higher pressure below pushes the plane up",

    "why do stars twinkle "
    "<THINK> stars appear to twinkle because of earths atmosphere "
    "starlight passes through layers of air with different temperatures and densities "
    "these layers bend and distort the light slightly "
    "the bending changes rapidly as air moves "
    "this makes the star appear to flicker "
    "planets do not twinkle as much because they are closer "
    "and appear as tiny discs rather than points of light </THINK> "
    "<ANSWER> stars twinkle because light bends as it passes through "
    "different layers of earths atmosphere "
    "planets twinkle less because they appear larger",

    "what causes earthquakes "
    "<THINK> earths surface is made of large pieces called tectonic plates "
    "these plates float on the molten mantle below "
    "they move very slowly but constantly "
    "when two plates get stuck against each other "
    "pressure builds up over time "
    "when the plates suddenly slip the energy releases as seismic waves "
    "these waves shake the ground causing an earthquake </THINK> "
    "<ANSWER> earthquakes are caused by tectonic plates "
    "when plates suddenly slip after building up pressure seismic waves shake the ground",

    # === NEW: INSTRUCTION FOLLOWING (5 more) ===
    "explain gravity simply "
    "<THINK> the user wants a simple explanation "
    "gravity is a force that pulls things together "
    "every object with mass pulls other objects toward it "
    "the heavier the object the stronger the pull "
    "on earth gravity pulls us toward the ground "
    "this is why things fall when you drop them </THINK> "
    "<ANSWER> gravity is a force that pulls objects toward each other "
    "earths gravity keeps us on the ground and makes things fall",

    "compare cats and dogs as pets "
    "<THINK> the user wants a comparison "
    "cats and dogs are both popular pets "
    "dogs are social and need walks and attention "
    "cats are more independent and clean themselves "
    "dogs can be trained more easily "
    "cats are better for people with busy schedules "
    "both make loving companions </THINK> "
    "<ANSWER> dogs are social and need more attention while cats are more independent "
    "dogs require walks and training while cats are lower maintenance "
    "both make wonderful pets depending on your lifestyle",

    "summarize what photosynthesis is "
    "<THINK> photosynthesis is a biological process "
    "plants use sunlight water and carbon dioxide "
    "they convert these into glucose for energy "
    "and release oxygen as a byproduct "
    "this process happens in the chloroplasts of plant cells "
    "chlorophyll is the green pigment that absorbs light </THINK> "
    "<ANSWER> photosynthesis is how plants make food "
    "they use sunlight water and carbon dioxide to produce glucose and oxygen",

    "what is the difference between weather and climate "
    "<THINK> weather and climate are related but different "
    "weather is the current atmospheric conditions "
    "temperature wind rain or sunshine on a given day "
    "climate is the average weather patterns over long periods "
    "usually 30 years or more "
    "a simple way to remember is weather is what you wear "
    "climate is what you expect to wear </THINK> "
    "<ANSWER> weather is daily atmospheric conditions like rain or sunshine "
    "climate is the average weather patterns over decades",

    "why is exercise important "
    "<THINK> the user wants to know about exercise benefits "
    "exercise has many health benefits "
    "it strengthens the heart and lungs "
    "it builds muscle and maintains healthy weight "
    "it releases chemicals in the brain that improve mood "
    "regular exercise reduces risk of heart disease diabetes and depression "
    "it also improves sleep quality </THINK> "
    "<ANSWER> exercise strengthens the heart muscles and lungs "
    "improves mood through brain chemicals "
    "and reduces risk of many diseases including heart disease and diabetes",

    # === NEW: MODUS TOLLENS / CONTRAPOSITIVE ===
    "the car needs fuel to run the car stopped moving does the car have fuel "
    "<THINK> step 1 cars need fuel to run "
    "step 2 if the car has no fuel it stops "
    "step 3 the car stopped "
    "step 4 therefore the most likely reason is it ran out of fuel </THINK> "
    "<ANSWER> no the car likely ran out of fuel because cars stop when they have no fuel",

    "if a number is even it is divisible by 2 the number 7 is not divisible by 2 is 7 even "
    "<THINK> step 1 even numbers are divisible by 2 "
    "step 2 7 divided by 2 is 3.5 which is not whole "
    "step 3 7 is not divisible by 2 "
    "step 4 therefore 7 is not an even number </THINK> "
    "<ANSWER> no 7 is not even because it is not divisible by 2",

    "plants need sunlight to grow the plant in the dark closet is dying why "
    "<THINK> step 1 plants make food using sunlight through photosynthesis "
    "step 2 a dark closet has no sunlight "
    "step 3 without sunlight the plant cannot make food "
    "step 4 without food the plant cannot survive </THINK> "
    "<ANSWER> the plant is dying because it has no sunlight and cannot perform photosynthesis",
]

"calculate 15% tip on a $45 meal <THINK> 10% of 45 is 4.5, 5% is 2.25, so 15% is 4.5 + 2.25 = 6.75 </THINK> <ANSWER> $6.75",

"convert 2.5 kilometers to miles <THINK> 1 km = 0.621371 miles, so 2.5 * 0.621371 = 1.553 miles </THINK> <ANSWER> about 1.55 miles",
