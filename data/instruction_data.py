# 30 instruction-following examples
# Format: instruction <THINK> reasoning </THINK> <ANSWER> response

instruction_data = [
    "summarize what gravity is "
    "<THINK> gravity is a force pulling objects together "
    "i should give a brief clear summary </THINK> "
    "<ANSWER> gravity is a force that attracts objects toward each other "
    "on earth it pulls everything toward the ground",

    "define photosynthesis "
    "<THINK> photosynthesis is how plants make food "
    "plants use sunlight water and co2 to make glucose and oxygen </THINK> "
    "<ANSWER> photosynthesis is the process plants use to convert "
    "sunlight water and carbon dioxide into glucose and oxygen",

    "explain what electricity is "
    "<THINK> electricity is the flow of electrons "
    "it powers our devices and runs through wires </THINK> "
    "<ANSWER> electricity is the flow of electrons through a conductor "
    "it powers devices lights and machines",

    "describe the water cycle "
    "<THINK> the water cycle has several stages "
    "water evaporates from oceans and lakes "
    "rises as water vapor condenses into clouds "
    "then falls as rain or snow back to earth </THINK> "
    "<ANSWER> the water cycle involves evaporation from oceans "
    "condensation into clouds and precipitation as rain or snow",

    "what is the difference between a planet and a star "
    "<THINK> planets and stars are very different "
    "stars produce their own light through nuclear fusion "
    "planets orbit stars and reflect light "
    "planets are much smaller than stars </THINK> "
    "<ANSWER> stars produce their own light through nuclear fusion "
    "planets orbit stars and only reflect light they do not produce it",

    "explain what a computer does "
    "<THINK> a computer processes information "
    "it takes input runs programs and produces output "
    "it stores data and follows instructions very quickly </THINK> "
    "<ANSWER> a computer processes information by following instructions "
    "it takes input runs programs stores data and produces output",

    "describe how the internet works "
    "<THINK> the internet is a global network "
    "computers connect through cables and wireless signals "
    "data is broken into packets sent across networks and reassembled </THINK> "
    "<ANSWER> the internet connects billions of computers worldwide "
    "data is broken into packets sent across networks and reassembled at the destination",

    "what is democracy "
    "<THINK> democracy is a system of government "
    "in a democracy citizens vote to choose their leaders "
    "decisions are made by majority rule "
    "with protections for individual rights </THINK> "
    "<ANSWER> democracy is a government system where citizens vote to choose leaders "
    "and decisions reflect the will of the majority",

    "explain what an ecosystem is "
    "<THINK> an ecosystem includes all living things in an area "
    "plus the non living environment "
    "plants animals soil water and air all interact "
    "each part depends on the others </THINK> "
    "<ANSWER> an ecosystem is all living organisms in an area "
    "plus their non living environment "
    "everything interacts and depends on each other",

    "define evolution "
    "<THINK> evolution is the change in species over time "
    "charles darwin described natural selection "
    "organisms with helpful traits survive and reproduce more "
    "over many generations species change and new species form </THINK> "
    "<ANSWER> evolution is the gradual change in species over generations "
    "driven by natural selection where helpful traits spread through populations",

    "what is a black hole "
    "<THINK> a black hole is an extremely dense region of space "
    "so dense that nothing not even light can escape its gravity "
    "they form when massive stars collapse "
    "the boundary is called the event horizon </THINK> "
    "<ANSWER> a black hole is an extremely dense region where gravity is so strong "
    "that nothing including light can escape "
    "they form from collapsed massive stars",

    "explain what climate change is "
    "<THINK> climate change refers to long term shifts in temperature and weather "
    "burning fossil fuels releases carbon dioxide "
    "this traps heat in the atmosphere "
    "causing global temperatures to rise "
    "leading to more extreme weather events </THINK> "
    "<ANSWER> climate change is the long term warming of earth "
    "caused by greenhouse gases from burning fossil fuels "
    "it causes more extreme weather events",

    "what is artificial intelligence "
    "<THINK> artificial intelligence is computer systems that perform tasks "
    "that normally require human intelligence "
    "like understanding language recognizing images or making decisions "
    "it learns from large amounts of data </THINK> "
    "<ANSWER> artificial intelligence is computer systems that perform tasks "
    "requiring human like intelligence "
    "such as understanding language recognizing images and making decisions",

    "describe what the immune system does "
    "<THINK> the immune system defends the body against disease "
    "it identifies foreign invaders like bacteria and viruses "
    "white blood cells attack and destroy pathogens "
    "antibodies remember past infections for faster response </THINK> "
    "<ANSWER> the immune system defends the body against pathogens "
    "white blood cells attack invaders "
    "and antibodies provide memory for faster future responses",

    "what is renewable energy "
    "<THINK> renewable energy comes from sources that naturally replenish "
    "solar energy comes from the sun "
    "wind energy from moving air "
    "hydroelectric from flowing water "
    "unlike fossil fuels these do not run out </THINK> "
    "<ANSWER> renewable energy comes from naturally replenishing sources "
    "like solar wind and water "
    "unlike fossil fuels they do not run out",

    "explain what dna is "
    "<THINK> dna stands for deoxyribonucleic acid "
    "it carries the genetic instructions for all living things "
    "it is stored in the nucleus of cells "
    "it determines traits like eye color and height "
    "it is passed from parents to children </THINK> "
    "<ANSWER> dna is the molecule that carries genetic instructions "
    "it determines traits and is passed from parents to children",

    "what is the big bang theory "
    "<THINK> the big bang theory explains the origin of the universe "
    "scientists believe the universe began about 13.8 billion years ago "
    "from an extremely hot dense point "
    "it expanded rapidly and has been expanding since "
    "forming galaxies stars and planets over billions of years </THINK> "
    "<ANSWER> the big bang theory says the universe began 13.8 billion years ago "
    "from a single hot dense point that rapidly expanded "
    "forming all matter space and time",

    "define supply and demand "
    "<THINK> supply and demand are economic concepts "
    "demand is how much people want something "
    "supply is how much is available "
    "when demand is high and supply is low prices rise "
    "when supply is high and demand is low prices fall </THINK> "
    "<ANSWER> supply is how much of something is available "
    "demand is how much people want it "
    "when demand exceeds supply prices rise "
    "when supply exceeds demand prices fall",

    "explain what a gene is "
    "<THINK> a gene is a segment of dna "
    "each gene contains instructions for making a protein "
    "proteins do most of the work in cells "
    "humans have about 20000 genes "
    "genes determine physical traits and biological functions </THINK> "
    "<ANSWER> a gene is a segment of dna that contains instructions for making a protein "
    "genes determine physical traits and biological functions",

    "what is gravity on the moon compared to earth "
    "<THINK> the moon is smaller than earth "
    "smaller mass means weaker gravity "
    "the moons gravity is about one sixth of earths "
    "this is why astronauts could jump very high on the moon "
    "a person weighing 60 kg on earth weighs 10 kg on the moon </THINK> "
    "<ANSWER> the moons gravity is about one sixth of earths "
    "so a person weighing 60 kg on earth would weigh only 10 kg on the moon",

    "describe the food chain "
    "<THINK> a food chain shows how energy flows through an ecosystem "
    "producers are plants that make food from sunlight "
    "primary consumers eat plants "
    "secondary consumers eat those animals "
    "and so on up the chain "
    "decomposers break down dead matter at the end </THINK> "
    "<ANSWER> a food chain shows energy flow from plants to animals "
    "plants are producers herbivores eat them "
    "carnivores eat herbivores "
    "and decomposers break down dead matter",

    "what is the speed of light "
    "<THINK> light travels at a constant speed in a vacuum "
    "this speed is about 300 million meters per second "
    "or about 186000 miles per second "
    "nothing with mass can travel as fast as light "
    "this is a fundamental constant of the universe </THINK> "
    "<ANSWER> light travels at about 300 million meters per second in a vacuum "
    "nothing with mass can travel this fast",

    "explain the water states of matter "
    "<THINK> water exists in three common states "
    "solid state is ice which forms at 0 celsius and below "
    "liquid state is water between 0 and 100 celsius "
    "gas state is water vapor or steam above 100 celsius "
    "changing state requires adding or removing heat energy </THINK> "
    "<ANSWER> water exists as solid ice liquid water or water vapor gas "
    "transitions between states require adding or removing heat",

    "what makes a good argument "
    "<THINK> a good argument has several qualities "
    "it starts with a clear claim or thesis "
    "it provides evidence to support the claim "
    "the evidence should be relevant and accurate "
    "it addresses counterarguments "
    "and reaches a logical conclusion </THINK> "
    "<ANSWER> a good argument has a clear claim supported by relevant evidence "
    "it addresses counterarguments and reaches a logical conclusion",

    "describe what happens during sleep "
    "<THINK> during sleep the body does important work "
    "the brain consolidates memories "
    "the body repairs cells and tissues "
    "the immune system strengthens "
    "growth hormone is released "
    "sleep cycles through rem and non rem stages "
    "rem sleep is when most dreaming occurs </THINK> "
    "<ANSWER> during sleep the brain consolidates memories "
    "the body repairs itself "
    "the immune system strengthens "
    "and the brain cycles through rem and non rem stages",

    "what is a scientific theory "
    "<THINK> a scientific theory is not just a guess "
    "it is an explanation supported by extensive evidence "
    "theories have been tested many times by many scientists "
    "they make accurate predictions that can be checked "
    "examples include gravity evolution and germ theory </THINK> "
    "<ANSWER> a scientific theory is a well tested explanation backed by extensive evidence "
    "it is much more than a guess "
    "examples include the theory of gravity and evolution",

    "explain what culture means "
    "<THINK> culture refers to the shared values and practices of a group "
    "it includes language traditions art music food and beliefs "
    "culture is learned and passed between generations "
    "different groups have different cultures "
    "culture shapes how people see the world </THINK> "
    "<ANSWER> culture is the shared values traditions language art and practices "
    "of a group of people "
    "it is learned and passed between generations",

    "what is inflation "
    "<THINK> inflation is the increase in prices over time "
    "when inflation is high money buys less than before "
    "it is caused by too much money in circulation "
    "or supply not keeping up with demand "
    "central banks try to control inflation </THINK> "
    "<ANSWER> inflation is the general rise in prices over time "
    "it means money buys less than it used to "
    "central banks try to keep it at low levels",

    "describe what a virus is "
    "<THINK> a virus is a tiny infectious agent "
    "it is smaller than bacteria "
    "viruses cannot reproduce on their own "
    "they need to infect a host cell "
    "they inject their genetic material into cells "
    "forcing them to make copies of the virus "
    "the immune system and vaccines help fight them </THINK> "
    "<ANSWER> a virus is a tiny infectious agent that needs a host cell to reproduce "
    "it injects genetic material into cells to make copies of itself",

    "explain what machine learning is "
    "<THINK> machine learning is a type of artificial intelligence "
    "instead of being explicitly programmed "
    "machine learning systems learn from data "
    "they find patterns in large datasets "
    "and improve their performance with experience "
    "examples include image recognition and language models </THINK> "
    "<ANSWER> machine learning is ai that learns from data rather than explicit programming "
    "systems find patterns and improve with experience "
    "used in image recognition language and recommendations",

    # List / enumerate examples
    "name three planets in our solar system "
    "<THINK> our solar system has eight planets mercury venus earth mars jupiter saturn uranus neptune i will name three </THINK> "
    "<ANSWER> three planets are earth mars and jupiter",

    "name two types of renewable energy "
    "<THINK> renewable energy comes from sources that replenish naturally solar and wind are common examples </THINK> "
    "<ANSWER> solar energy and wind energy are two types of renewable energy",

    "list the three states of matter "
    "<THINK> matter can exist in three common states solid liquid and gas each has different properties </THINK> "
    "<ANSWER> the three states of matter are solid liquid and gas",

    "name three primary colors "
    "<THINK> in traditional color theory the three primary colors are red blue and yellow they cannot be made by mixing other colors </THINK> "
    "<ANSWER> the three primary colors are red blue and yellow",

    "give two examples of mammals "
    "<THINK> mammals are warm blooded animals that have fur and feed their young milk dogs and whales are examples </THINK> "
    "<ANSWER> dogs and whales are two examples of mammals",

    "name the four seasons "
    "<THINK> the four seasons are caused by earths tilt they are spring summer autumn and winter </THINK> "
    "<ANSWER> the four seasons are spring summer autumn and winter",

    "list three things that need water to survive "
    "<THINK> water is essential for life plants animals and humans all need water to survive </THINK> "
    "<ANSWER> plants animals and humans all need water to survive",

    "name two planets larger than earth "
    "<THINK> earth is medium sized in our solar system jupiter and saturn are much larger </THINK> "
    "<ANSWER> jupiter and saturn are two planets larger than earth",

    "give one example of a gas "
    "<THINK> gases are substances that expand to fill their container oxygen and nitrogen are common gases oxygen is in the air we breathe </THINK> "
    "<ANSWER> oxygen is an example of a gas",

    "list two things that produce light "
    "<THINK> light can be produced by the sun and by electric light bulbs both are common sources </THINK> "
    "<ANSWER> the sun and electric light bulbs are two things that produce light",
]
