return {
    ["TopLevelOne"]= "Default",
    ["nodes"]= {
        [33]= {
            ["icon"]= "Art/2DArt/SkillIcons/passives/NotableBlank.png",
            ["name"]= "Unknown Notable",
            ["skill"]= 33,
            ["stats"]= {},
            ["isNotable"]= true
        },
        [240]= {
            ["in"]= {
                "7555"
            },
            ["out"]= {},
            ["icon"]= "Art/2DArt/SkillIcons/passives/MasteryBlank.png",
            ["name"]= "Unknown Mastery",
            ["group"]= 258,
            ["orbit"]= 0,
            ["skill"]= 240,
            ["stats"]= {},
            ["isMastery"]= true,
            ["activeIcon"]= "Art/2DArt/SkillIcons/passives/MasteryBlank.png",
            ["orbitIndex"]= 0,
            ["inactiveIcon"]= "Art/2DArt/SkillIcons/passives/MasteryBlank.png",
            ["masteryEffects"]= {
                {
                    ["stats"]= {
                        "40% of Physical Damage Converted to Lightning Damage"
                    },
                    ["effect"]= 53046
                },
                {
                    ["stats"]= {
                        "60% increased Critical Strike Chance against enemies with Lightning Exposure"
                    },
                    ["effect"]= 64241
                },
                {
                    ["stats"]= {
                        "+15% to Maximum Effect of Shock"
                    },
                    ["effect"]= 50993,
                    ["reminderText"]= {
                        "(Base Maximum Effect of Shock is 50% increased Damage taken)"
                    }
                },
                {
                    ["stats"]= {
                        "Shocks you inflict spread to other Enemies within 1 metre"
                    },
                    ["effect"]= 28569
                },
                {
                    ["stats"]= {
                        "Increases and reductions to Maximum Mana also apply to Shock Effect at 30% of their value"
                    },
                    ["effect"]= 64063
                },
                {
                    ["stats"]= {
                        "Lightning Damage of Enemies Hitting you while you're Shocked is Unlucky"
                    },
                    ["effect"]= 20364,
                    ["reminderText"]= {
                        "(Unlucky things are rolled twice and the worst result used)"
                    }
                },
                {
                    ["stats"]= {
                        "10% more Maximum Life if you have at least 6 Life Masteries allocated"
                    },
                    ["effect"]= 64381
                },
                {
                    ["stats"]= {
                        "15% increased maximum Life if there are no Life Modifiers on Equipped Body Armour"
                    },
                    ["effect"]= 34242
                },
                {
                    ["stats"]= {
                        "+50 to maximum Life"
                    },
                    ["effect"]= 47642
                },
                {
                    ["stats"]= {
                        "You count as on Low Life while at 55% of maximum Life or below"
                    },
                    ["effect"]= 31822
                },
                {
                    ["stats"]= {
                        "You count as on Full Life while at 90% of maximum Life or above"
                    },
                    ["effect"]= 21468
                },
                {
                    ["stats"]= {
                        "Skills Cost Life instead of 30% of Mana Cost"
                    },
                    ["effect"]= 38454
                }
            },
            ["activeEffectImage"]= "Art/2DArt/UIImages/InGame/PassiveMastery/MasteryBackgroundGraphic/MasteryLightningPattern.png"
        },
        [258]= {
            ["in"]= {
                "47873"
            },
            ["out"]= {},
            ["icon"]= "Art/2DArt/SkillIcons/passives/MasteryBlank.png",
            ["name"]= "Unknown Ascendancy Node",
            ["group"]= 320,
            ["orbit"]= 4,
            ["skill"]= 258,
            ["stats"]= {},
            ["isNotable"]= true,
            ["orbitIndex"]= 11,
            ["ascendancyName"]= "None"
        },
        [2311]= {
            ["in"]= {
                "13201"
            },
            ["out"]= {
                "7956"
            },
            ["icon"]= "Art/2DArt/SkillIcons/passives/MasteryBlank.png",
            ["name"]= "Small Jewel Socket",
            ["group"]= 176,
            ["orbit"]= 2,
            ["skill"]= 2311,
            ["stats"]= {},
            ["orbitIndex"]= 1,
            ["isJewelSocket"]= true,
            ["expansionJewel"]= {
                ["size"]= 0,
                ["index"]= 0,
                ["proxy"]= "7956",
                ["parent"]= "9408"
            }
        },
        [367]= {
            ["in"]= {
                "35706",
                "14021"
            },
            ["out"]= {
                "33864"
            },
            ["icon"]= "Art/2DArt/SkillIcons/passives/energyshield.png",
            ["name"]= "Unknown Normal Node",
            ["group"]= 239,
            ["orbit"]= 2,
            ["skill"]= 367,
            ["stats"]= {},
            ["orbitIndex"]= 5
        },
	},
    ["classes"]= {
        {
            ["name"]= "Scion",
            ["base_dex"]= 20,
            ["base_int"]= 20,
            ["base_str"]= 20,
            ["ascendancies"]= {
                {
                    ["id"]= "Ascendant",
                    ["name"]= "Ascendant"
                }
            }
        },
        {
            ["name"]= "Marauder",
            ["base_dex"]= 14,
            ["base_int"]= 14,
            ["base_str"]= 32,
            ["ascendancies"]= {
                {
                    ["id"]= "Juggernaut",
                    ["name"]= "Juggernaut",
                    ["flavourText"]= "     What divides the conqueror \n from the conquered? Perseverance.",
                    ["flavourTextRect"]= {
                        ["x"]= 215,
                        ["y"]= 165,
                        ["width"]= 1063,
                        ["height"]= 436
                    },
                    ["flavourTextColour"]= "af5a32"
                },
                {
                    ["id"]= "Berserker",
                    ["name"]= "Berserker",
                    ["flavourText"]= "The savage path is \nalways swift and sure.",
                    ["flavourTextRect"]= {
                        ["x"]= 760,
                        ["y"]= 345,
                        ["width"]= 976,
                        ["height"]= 429
                    },
                    ["flavourTextColour"]= "af5a32"
                },
                {
                    ["id"]= "Chieftain",
                    ["name"]= "Chieftain",
                    ["flavourText"]= "   The Ancestors speak \nthrough your clenched fists.",
                    ["flavourTextRect"]= {
                        ["x"]= 185,
                        ["y"]= 245,
                        ["width"]= 1076,
                        ["height"]= 449
                    },
                    ["flavourTextColour"]= "af5a32"
                }
            }
        },
        {
            ["name"]= "Ranger",
            ["base_dex"]= 32,
            ["base_int"]= 14,
            ["base_str"]= 14,
            ["ascendancies"]= {
                {
                    ["id"]= "Raider",
                    ["name"]= "Raider",
                    ["flavourText"]= "No hunt is complete without\nthe gutting and the skinning.",
                    ["flavourTextRect"]= {
                        ["x"]= 365,
                        ["y"]= 965,
                        ["width"]= 900,
                        ["height"]= 1250
                    },
                    ["flavourTextColour"]= "7cb376"
                },
                {
                    ["id"]= "Deadeye",
                    ["name"]= "Deadeye",
                    ["flavourText"]= "A woman can change the world \nwith a single well-placed arrow.",
                    ["flavourTextRect"]= {
                        ["x"]= 335,
                        ["y"]= 1045,
                        ["width"]= 870,
                        ["height"]= 1330
                    },
                    ["flavourTextColour"]= "7cb376"
                },
                {
                    ["id"]= "Pathfinder",
                    ["name"]= "Pathfinder",
                    ["flavourText"]= "There are venoms and virtues aplenty in \n the wilds, if you know where to look.",
                    ["flavourTextRect"]= {
                        ["x"]= 265,
                        ["y"]= 975,
                        ["width"]= 900,
                        ["height"]= 1250
                    },
                    ["flavourTextColour"]= "7cb376"
                }
            }
        },
        {
            ["name"]= "Witch",
            ["base_dex"]= 14,
            ["base_int"]= 32,
            ["base_str"]= 14,
            ["ascendancies"]= {
                {
                    ["id"]= "Occultist",
                    ["name"]= "Occultist",
                    ["flavourText"]= " Throw off the chains\nof fear and embrace that\n which was forbidden.",
                    ["flavourTextRect"]= {
                        ["x"]= 665,
                        ["y"]= 385,
                        ["width"]= 906,
                        ["height"]= 389
                    },
                    ["flavourTextColour"]= "9ac3c9"
                },
                {
                    ["id"]= "Elementalist",
                    ["name"]= "Elementalist",
                    ["flavourText"]= "Feed a storm with savage intent \nand not even the strongest walls\nwill hold it back.",
                    ["flavourTextRect"]= {
                        ["x"]= 125,
                        ["y"]= 475,
                        ["width"]= 510,
                        ["height"]= 768
                    },
                    ["flavourTextColour"]= "9ac3c9"
                },
                {
                    ["id"]= "Necromancer",
                    ["name"]= "Necromancer",
                    ["flavourText"]= "Embrace the serene\npower that is undeath.",
                    ["flavourTextRect"]= {
                        ["x"]= 720,
                        ["y"]= 303,
                        ["width"]= 1000,
                        ["height"]= 1000
                    },
                    ["flavourTextColour"]= "9ac3c9"
                }
            }
        },
        {
            ["name"]= "Duelist",
            ["base_dex"]= 23,
            ["base_int"]= 14,
            ["base_str"]= 23,
            ["ascendancies"]= {
                {
                    ["id"]= "Slayer",
                    ["name"]= "Slayer",
                    ["flavourText"]= " No judge. No jury.\nJust the executioner.",
                    ["flavourTextRect"]= {
                        ["x"]= 470,
                        ["y"]= 310,
                        ["width"]= 976,
                        ["height"]= 429
                    },
                    ["flavourTextColour"]= "96afc8"
                },
                {
                    ["id"]= "Gladiator",
                    ["name"]= "Gladiator",
                    ["flavourText"]= "Raise your hand to the \nroaring crowd and pledge \nyour allegiance to glory.",
                    ["flavourTextRect"]= {
                        ["x"]= 670,
                        ["y"]= 395,
                        ["width"]= 976,
                        ["height"]= 429
                    },
                    ["flavourTextColour"]= "96afc8"
                },
                {
                    ["id"]= "Champion",
                    ["name"]= "Champion",
                    ["flavourText"]= "Champion that which \n you love. He who fights\n for nothing, dies\n for nothing.",
                    ["flavourTextRect"]= {
                        ["x"]= 735,
                        ["y"]= 625,
                        ["width"]= 976,
                        ["height"]= 429
                    },
                    ["flavourTextColour"]= "96afc8"
                }
            }
        },
        {
            ["name"]= "Templar",
            ["base_dex"]= 14,
            ["base_int"]= 23,
            ["base_str"]= 23,
            ["ascendancies"]= {
                {
                    ["id"]= "Inquisitor",
                    ["name"]= "Inquisitor",
                    ["flavourText"]= " Truth is elusive, yet God has\nprovided us with all the tools \n necessary to find it.",
                    ["flavourTextRect"]= {
                        ["x"]= 285,
                        ["y"]= 940,
                        ["width"]= 926,
                        ["height"]= 429
                    },
                    ["flavourTextColour"]= "cfbd8a"
                },
                {
                    ["id"]= "Hierophant",
                    ["name"]= "Hierophant",
                    ["flavourText"]= "Drink deeply from God's\n chalice, for the faithful\n will never find it empty.",
                    ["flavourTextRect"]= {
                        ["x"]= 100,
                        ["y"]= 720,
                        ["width"]= 936,
                        ["height"]= 399
                    },
                    ["flavourTextColour"]= "cfbd8a"
                },
                {
                    ["id"]= "Guardian",
                    ["name"]= "Guardian",
                    ["flavourText"]= "When bound by faith\n and respect, the flock\n will overwhelm the wolf.",
                    ["flavourTextRect"]= {
                        ["x"]= 170,
                        ["y"]= 780,
                        ["width"]= 976,
                        ["height"]= 429
                    },
                    ["flavourTextColour"]= "cfbd8a"
                }
            }
        },
        {
            ["name"]= "Shadow",
            ["base_dex"]= 23,
            ["base_int"]= 23,
            ["base_str"]= 14,
            ["ascendancies"]= {
                {
                    ["id"]= "Assassin",
                    ["name"]= "Assassin",
                    ["flavourText"]= "Death is a banquet. \n It's up to the murderer \n to write the menu.",
                    ["flavourTextRect"]= {
                        ["x"]= 650,
                        ["y"]= 845,
                        ["width"]= 976,
                        ["height"]= 429
                    },
                    ["flavourTextColour"]= "72818d"
                },
                {
                    ["id"]= "Trickster",
                    ["name"]= "Trickster",
                    ["flavourText"]= "  Everyone knows how to die. \n Some just need a little nudge \nto get them started.",
                    ["flavourTextRect"]= {
                        ["x"]= 315,
                        ["y"]= 150,
                        ["width"]= 976,
                        ["height"]= 429
                    },
                    ["flavourTextColour"]= "72818d"
                },
                {
                    ["id"]= "Saboteur",
                    ["name"]= "Saboteur",
                    ["flavourText"]= "The artist need not be present \n to make a lasting impression.",
                    ["flavourTextRect"]= {
                        ["x"]= 355,
                        ["y"]= 970,
                        ["width"]= 976,
                        ["height"]= 429
                    },
                    ["flavourTextColour"]= "72818d"
                }
            }
        }
    },
    ["imageZoomLevels"]= {
        0.1246,
        0.2109,
        0.2972,
        0.3835
    },
    ["points"]= {
        ["totalPoints"]= 123,
        ["ascendancyPoints"]= 8
    }
}