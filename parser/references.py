from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass


@dataclass
class QualifierReference:
    qualifier_id: int
    name: str
    value_type: str
    description: str


class OptaEventTypeReference:
    EVENT_TYPES = {
        1: {
            "name": "Pass",
            "description": "Any pass attempted from one player to another",
        },
        2: {
            "name": "Offside Pass",
            "description": "Attempted pass to player in offside position",
        },
        3: {"name": "Take On", "description": "Attempted dribble past opponent"},
        4: {"name": "Foul", "description": "Foul committed resulting in free kick"},
        5: {"name": "Out", "description": "Ball goes out for throw-in or goal kick"},
        6: {"name": "Corner Awarded", "description": "Ball goes out for corner kick"},
        7: {"name": "Tackle", "description": "Dispossess opponent of ball"},
        8: {"name": "Interception", "description": "Intercept pass between opposition"},
        9: {
            "name": "Turnover",
            "description": "Unforced error/loss of possession (NO LONGER USED)",
        },
        10: {"name": "Save", "description": "Goalkeeper saves shot"},
        11: {"name": "Claim", "description": "Goalkeeper catches crossed ball"},
        12: {"name": "Clearance", "description": "Clear ball from defensive zone"},
        13: {"name": "Miss", "description": "Shot wide or over goal"},
        14: {"name": "Post", "description": "Ball hits frame of goal"},
        15: {"name": "Attempt Saved", "description": "Shot saved"},
        16: {"name": "Goal", "description": "Goal scored"},
        17: {"name": "Card", "description": "Yellow or red card shown"},
        18: {"name": "Player off", "description": "Substitution off"},
        19: {"name": "Player on", "description": "Substitution on"},
        20: {"name": "Player retired", "description": "Player forced to leave pitch"},
        21: {"name": "Player returns", "description": "Player returns after injury"},
        22: {
            "name": "Player becomes goalkeeper",
            "description": "Outfield player replaces GK",
        },
        23: {
            "name": "Goalkeeper becomes player",
            "description": "GK becomes outfield player",
        },
        24: {"name": "Condition change", "description": "Change in playing conditions"},
        25: {"name": "Official change", "description": "Referee or linesman replaced"},
        27: {"name": "Start delay", "description": "Stoppage in play"},
        28: {"name": "End delay", "description": "Stoppage ends, play resumes"},
        30: {"name": "End", "description": "End of match period"},
        32: {"name": "Start", "description": "Start of match period"},
        34: {
            "name": "Team set up",
            "description": "Team lineup; qualifiers show formation",
        },
        35: {
            "name": "Player changed position",
            "description": "Player moved to different position",
        },
        36: {
            "name": "Player changed Jersey number",
            "description": "Player forced to change shirt",
        },
        37: {"name": "Collection End", "description": "End of match data collection"},
        38: {"name": "Temp_Goal", "description": "Goal pending additional qualifiers"},
        39: {
            "name": "Temp_Attempt",
            "description": "Shot pending additional qualifiers",
        },
        40: {"name": "Formation change", "description": "Team alters formation"},
        41: {"name": "Punch", "description": "Goalkeeper punches ball clear"},
        42: {"name": "Good Skill", "description": "Good skill shown (NO LONGER USED)"},
        43: {"name": "Deleted event", "description": "Event deleted"},
        44: {"name": "Aerial", "description": "Aerial duel (50/50)"},
        45: {"name": "Challenge", "description": "Player fails to win ball in dribble"},
        47: {"name": "Rescinded card", "description": "Card rescinded post-match"},
        49: {"name": "Ball recovery", "description": "Team wins possession"},
        50: {"name": "Dispossessed", "description": "Player loses possession"},
        51: {"name": "Error", "description": "Player mistake losing ball"},
        52: {"name": "Keeper pick-up", "description": "Goalkeeper picks up ball"},
        53: {"name": "Cross not claimed", "description": "GK fails to catch cross"},
        54: {"name": "Smother", "description": "GK covers ball in box"},
        55: {"name": "Offside provoked", "description": "Defender triggers offside"},
        56: {
            "name": "Shield ball opp",
            "description": "Defender shields ball from opponent",
        },
        57: {"name": "Foul throw-in", "description": "Throw-in taken incorrectly"},
        58: {"name": "Penalty faced", "description": "GK faces penalty"},
        59: {"name": "Keeper Sweeper", "description": "Keeper off line to clear ball"},
        60: {
            "name": "Chance missed",
            "description": "Player in good position doesn't receive pass",
        },
        61: {"name": "Ball touch", "description": "Bad touch losing possession"},
        63: {"name": "Temp_Save", "description": "Save without full details"},
        64: {"name": "Resume", "description": "Match resumes after abandonment"},
        65: {
            "name": "Contentious referee decision",
            "description": "Major talking point by ref",
        },
        66: {"name": "Possession Data", "description": "Possession event every 5 mins"},
        67: {"name": "50/50", "description": "Duel for loose ball (GERMAN ONLY)"},
        68: {"name": "Referee Drop Ball", "description": "Ref stops, drops ball"},
        69: {"name": "Failed to Block", "description": "Attempt to block lost"},
        70: {"name": "Injury Time Announcement", "description": "Injury time awarded"},
        71: {"name": "Coach Setup", "description": "Coach type event"},
        72: {"name": "Caught Offside", "description": "Player in offside position"},
        73: {"name": "Other Ball Contact", "description": "Automated DFL event"},
        74: {"name": "Blocked Pass", "description": "Defender blocks pass"},
    }

    @classmethod
    def get_type_name(cls, type_id: int) -> str:
        return cls.EVENT_TYPES.get(type_id, {}).get("name", f"Unknown (ID: {type_id})")

    @classmethod
    def get_type_description(cls, type_id: int) -> str:
        return cls.EVENT_TYPES.get(type_id, {}).get("description", "No description")


class OptaQualifierReference:
    QUALIFIERS = {
        1: QualifierReference(1, "Long ball", "Boolean", "Pass over 35 yards"),
        2: QualifierReference(2, "Cross", "Boolean", "Ball from wide areas into box"),
        3: QualifierReference(3, "Head pass", "Boolean", "Pass made with head"),
        4: QualifierReference(4, "Through ball", "Boolean", "Ball for attacking run"),
        5: QualifierReference(5, "Free kick taken", "Boolean", "Free kick taken"),
        6: QualifierReference(6, "Corner taken", "Boolean", "Corner kick taken"),
        7: QualifierReference(
            7, "Players caught offside", "Player ID", "Player in offside"
        ),
        8: QualifierReference(
            8, "Goal disallowed", "Boolean", "Pass led to disallowed goal"
        ),
        9: QualifierReference(9, "Penalty", "Boolean", "Penalty kick"),
        15: QualifierReference(15, "Head", "Boolean", "Action with head"),
        20: QualifierReference(20, "Right footed", "Boolean", "Shot with right foot"),
        21: QualifierReference(
            21, "Other body part", "Boolean", "Shot with other body part"
        ),
        28: QualifierReference(28, "Own goal", "Boolean", "Own goal"),
        29: QualifierReference(29, "Assisted", "Boolean", "Shot had assist"),
        30: QualifierReference(30, "Involved", "Player IDs", "Players in lineup"),
        31: QualifierReference(31, "Yellow card", "Boolean", "Yellow card shown"),
        32: QualifierReference(32, "Second yellow", "Boolean", "Second yellow card"),
        33: QualifierReference(33, "Red card", "Boolean", "Red card shown"),
        34: QualifierReference(34, "Referee abuse", "Boolean", "Card for abuse to ref"),
        35: QualifierReference(35, "Argument", "Boolean", "Card for argument"),
        36: QualifierReference(36, "Fight", "Boolean", "Card for fight"),
        37: QualifierReference(37, "Time wasting", "Boolean", "Card for time wasting"),
        38: QualifierReference(
            38, "Excessive celebration", "Boolean", "Card for celebration"
        ),
        39: QualifierReference(
            39, "Crowd interaction", "Boolean", "Card for crowd contact"
        ),
        40: QualifierReference(
            40, "Other reason", "Boolean", "Card for unknown reason"
        ),
        41: QualifierReference(41, "Injury", "Boolean", "Substitution for injury"),
        42: QualifierReference(42, "Tactical", "Boolean", "Substitution for tactics"),
        44: QualifierReference(44, "Player position", "Text", "GK/DEF/MID/FWD/SUB"),
        50: QualifierReference(
            50, "Official position", "1-4", "Referee/Linesman positions"
        ),
        51: QualifierReference(51, "Official ID", "ID", "Unique official ID"),
        53: QualifierReference(53, "Injured player ID", "Player ID", "Injured player"),
        54: QualifierReference(54, "End cause", "1-100", "Reason for match end"),
        56: QualifierReference(56, "Zone", "Text", "Back/Left/Centre/Right"),
        57: QualifierReference(57, "End type", "Type", "End of match period"),
        59: QualifierReference(59, "Jersey number", "Integer", "Shirt number"),
        72: QualifierReference(72, "Left footed", "Boolean", "Shot with left foot"),
        88: QualifierReference(88, "High claim", "Boolean", "GK high claim"),
        89: QualifierReference(89, "1 on 1", "Boolean", "Attacker 1-on-1 with GK"),
        90: QualifierReference(90, "Deflected save", "Boolean", "GK deflected save"),
        91: QualifierReference(
            91, "Dive and deflect", "Boolean", "GK dive and deflect"
        ),
        92: QualifierReference(92, "Catch", "Boolean", "GK catches"),
        93: QualifierReference(93, "Dive and catch", "Boolean", "GK dive and catch"),
        95: QualifierReference(95, "Back pass", "Boolean", "Illegal GK back pass"),
        106: QualifierReference(
            106, "Attacking pass", "Boolean", "Pass in opposition half"
        ),
        107: QualifierReference(107, "Throw-in", "Boolean", "Throw-in taken"),
        108: QualifierReference(108, "Volley", "Boolean", "Shot on volley"),
        109: QualifierReference(109, "Overhead", "Boolean", "Overhead kick"),
        113: QualifierReference(113, "Strong", "Boolean", "Strong shot"),
        114: QualifierReference(114, "Weak", "Boolean", "Weak shot"),
        115: QualifierReference(115, "Rising", "Boolean", "Rising shot"),
        116: QualifierReference(116, "Dipping", "Boolean", "Dipping shot"),
        117: QualifierReference(117, "Lob", "Boolean", "Lob attempt"),
        120: QualifierReference(120, "Swerve left", "Boolean", "Swerve left"),
        121: QualifierReference(121, "Swerve right", "Boolean", "Swerve right"),
        122: QualifierReference(122, "Swerve moving", "Boolean", "Multiple swerves"),
        123: QualifierReference(123, "Keeper throw", "Boolean", "GK throws"),
        124: QualifierReference(124, "Goal kick", "Boolean", "Goal kick taken"),
        128: QualifierReference(128, "Punch", "Boolean", "GK punches"),
        130: QualifierReference(
            130, "Team formation", "Formation ID", "Team formation"
        ),
        131: QualifierReference(
            131, "Team player formation", "1-11", "Player formation slot"
        ),
        132: QualifierReference(132, "Dive", "Boolean", "Simulation/dive"),
        133: QualifierReference(133, "Deflection", "Boolean", "Shot deflection"),
        136: QualifierReference(136, "Keeper touched", "Boolean", "GK touched goal"),
        137: QualifierReference(137, "Keeper saved", "Boolean", "GK saved wide shot"),
        138: QualifierReference(138, "Hit woodwork", "Boolean", "Hit post/bar"),
        139: QualifierReference(139, "Own player", "Boolean", "Shot saved by defender"),
        140: QualifierReference(140, "Pass End X", "0-100", "X coordinate of pass end"),
        141: QualifierReference(141, "Pass End Y", "0-100", "Y coordinate of pass end"),
        144: QualifierReference(
            144, "Deleted event type", "Event ID", "Event to remove"
        ),
        152: QualifierReference(152, "Direct", "Boolean", "Direct free kick"),
        153: QualifierReference(153, "Not past goal line", "Boolean", "Shot missed"),
        154: QualifierReference(
            154, "Intentional assist", "Boolean", "Intentional assist"
        ),
        155: QualifierReference(155, "Chipped", "Boolean", "Chipped pass"),
        156: QualifierReference(156, "Lay-off", "Boolean", "Lay-off pass"),
        157: QualifierReference(157, "Launch", "Boolean", "Launch pass"),
        158: QualifierReference(
            158, "Persistent infringement", "Boolean", "Persistent foul"
        ),
        159: QualifierReference(159, "Foul language", "Boolean", "Foul language"),
        160: QualifierReference(
            160, "Throw-in set piece", "Boolean", "Throw-in set piece"
        ),
        161: QualifierReference(161, "Encroachment", "Boolean", "Encroachment"),
        162: QualifierReference(162, "Leaving field", "Boolean", "Leaving field"),
        163: QualifierReference(163, "Entering field", "Boolean", "Entering field"),
        164: QualifierReference(164, "Spitting", "Boolean", "Spitting"),
        165: QualifierReference(
            165, "Professional foul", "Boolean", "Professional foul"
        ),
        166: QualifierReference(166, "Handling on line", "Boolean", "Handball block"),
        168: QualifierReference(168, "Flick-on", "Boolean", "Flick-on pass"),
        171: QualifierReference(171, "Rescinded card", "Boolean", "Card rescinded"),
        172: QualifierReference(
            172, "No impact on timing", "Boolean", "Booked off bench"
        ),
        173: QualifierReference(173, "Parried safe", "Boolean", "GK parries safe"),
        174: QualifierReference(
            174, "Parried danger", "Boolean", "GK parries to danger"
        ),
        175: QualifierReference(175, "Fingertip", "Boolean", "GK fingertip save"),
        176: QualifierReference(176, "Caught", "Boolean", "GK catches"),
        177: QualifierReference(177, "Collected", "Boolean", "GK collects"),
        178: QualifierReference(178, "Standing", "Boolean", "GK standing save"),
        179: QualifierReference(179, "Diving", "Boolean", "GK diving save"),
        180: QualifierReference(180, "Stooping", "Boolean", "GK stooping save"),
        181: QualifierReference(181, "Reaching", "Boolean", "GK reaching save"),
        182: QualifierReference(182, "Hands", "Boolean", "GK saves with hands"),
        183: QualifierReference(183, "Feet", "Boolean", "GK saves with feet"),
        184: QualifierReference(184, "Dissent", "Boolean", "Card for dissent"),
        186: QualifierReference(186, "Scored", "Stat", "Shot not saved = goal"),
        187: QualifierReference(187, "Saved", "Stat", "Shot saved"),
        188: QualifierReference(188, "Missed", "Stat", "Shot missed"),
        189: QualifierReference(189, "Player not visible", "Boolean", "Replay shown"),
        191: QualifierReference(191, "Off ball foul", "Boolean", "Off-ball foul"),
        192: QualifierReference(192, "Block by hand", "Boolean", "Block by hand"),
        194: QualifierReference(194, "Captain", "Player ID", "Team captain ID"),
        195: QualifierReference(195, "Pull back", "Boolean", "Pull back pass"),
        196: QualifierReference(196, "Switch of play", "Boolean", "Switch of play"),
        197: QualifierReference(197, "Team kit", "Kit ID", "Team kit ID"),
        198: QualifierReference(198, "GK hoof", "Boolean", "GK kicks long"),
        199: QualifierReference(
            199, "GK kick from hands", "Boolean", "GK kicks from hands"
        ),
        200: QualifierReference(200, "Referee stop", "Boolean", "Referee stops"),
        201: QualifierReference(201, "Referee delay", "Boolean", "Referee delay"),
        202: QualifierReference(202, "Weather problem", "Boolean", "Weather stoppage"),
        203: QualifierReference(203, "Crowd trouble", "Boolean", "Crowd trouble"),
        204: QualifierReference(204, "Fire", "Boolean", "Fire in stadium"),
        205: QualifierReference(205, "Object thrown", "Boolean", "Object from crowd"),
        206: QualifierReference(
            206, "Spectator on pitch", "Boolean", "Spectator on pitch"
        ),
        207: QualifierReference(
            207, "Awaiting decision", "Boolean", "Awaiting decision"
        ),
        208: QualifierReference(208, "Referee injury", "Boolean", "Referee injury"),
        209: QualifierReference(209, "Game end", "Boolean", "Game finished"),
        210: QualifierReference(210, "Assist", "Boolean", "Pass is assist"),
        212: QualifierReference(212, "Length", "Yards", "Pass distance in yards"),
        213: QualifierReference(213, "Angle", "Radians", "Ball angle (0-6.28)"),
        214: QualifierReference(214, "Big chance", "Boolean", "Big chance"),
        215: QualifierReference(215, "Individual play", "Boolean", "Individual play"),
        217: QualifierReference(217, "2nd assisted", "Boolean", "2nd assist"),
        218: QualifierReference(218, "2nd assist", "Boolean", "Pass created assist"),
        219: QualifierReference(
            219, "Players on both posts", "Boolean", "Both posts covered"
        ),
        220: QualifierReference(
            220, "Player on near post", "Boolean", "Near post covered"
        ),
        221: QualifierReference(
            221, "Player on far post", "Boolean", "Far post covered"
        ),
        222: QualifierReference(
            222, "No players on posts", "Boolean", "Posts uncovered"
        ),
        223: QualifierReference(223, "In-swinger", "Boolean", "Corner in-swinger"),
        224: QualifierReference(224, "Out-swinger", "Boolean", "Corner out-swinger"),
        225: QualifierReference(225, "Straight", "Boolean", "Corner straight"),
        226: QualifierReference(226, "Suspended", "Boolean", "Game suspended"),
        227: QualifierReference(227, "Resume", "Boolean", "Game resumed"),
        228: QualifierReference(228, "Own shot blocked", "Boolean", "Own shot blocked"),
        230: QualifierReference(230, "GK X coordinate", "Coordinate", "GK position X"),
        231: QualifierReference(231, "GK Y coordinate", "Coordinate", "GK position Y"),
        236: QualifierReference(236, "Blocked pass", "Boolean", "Blocked pass"),
        237: QualifierReference(237, "Low", "Boolean", "Low goal kick"),
        238: QualifierReference(238, "Fair play", "Boolean", "Fair play kick"),
        240: QualifierReference(240, "GK start", "Boolean", "GK passes from hands"),
        241: QualifierReference(241, "Indirect", "Boolean", "Indirect free kick"),
        242: QualifierReference(242, "Obstruction", "Boolean", "Obstruction foul"),
        243: QualifierReference(243, "Unsporting behavior", "Boolean", "Unsporting"),
        244: QualifierReference(244, "Not retreating", "Boolean", "Not retreating"),
        245: QualifierReference(245, "Serious foul", "Boolean", "Serious foul"),
        246: QualifierReference(246, "Drinks break", "Boolean", "Drinks break"),
        254: QualifierReference(254, "Follows dribble", "Boolean", "Follows dribble"),
        255: QualifierReference(255, "Open roof", "Boolean", "Roof open"),
        256: QualifierReference(256, "Air humidity", "Percent", "Humidity %"),
        257: QualifierReference(257, "Air pressure", "Value", "Air pressure"),
        258: QualifierReference(258, "Sold out", "Boolean", "Stadium sold out"),
        259: QualifierReference(259, "Celsius degrees", "Temperature", "Temperature C"),
        260: QualifierReference(260, "Floodlight", "Boolean", "Floodlit"),
        261: QualifierReference(261, "1 on 1 chip", "Boolean", "1v1 chip goal"),
        262: QualifierReference(262, "Back heel", "Boolean", "Back heel goal"),
        263: QualifierReference(263, "Direct corner", "Boolean", "Direct corner goal"),
        264: QualifierReference(264, "Aerial foul", "Boolean", "Aerial foul"),
        265: QualifierReference(265, "Attempted tackle", "Boolean", "Tackle attempt"),
        266: QualifierReference(266, "Put through", "Boolean", "Put through"),
        267: QualifierReference(
            267, "Right arm save", "Boolean", "Saved with right arm"
        ),
        268: QualifierReference(268, "Left arm save", "Boolean", "Saved with left arm"),
        269: QualifierReference(
            269, "Both arms save", "Boolean", "Saved with both arms"
        ),
        270: QualifierReference(
            270, "Right leg save", "Boolean", "Saved with right leg"
        ),
        271: QualifierReference(271, "Left leg save", "Boolean", "Saved with left leg"),
        272: QualifierReference(
            272, "Both legs save", "Boolean", "Saved with both legs"
        ),
        273: QualifierReference(273, "Hit right post", "Boolean", "Hit right post"),
        274: QualifierReference(274, "Hit left post", "Boolean", "Hit left post"),
        275: QualifierReference(275, "Hit bar", "Boolean", "Hit crossbar"),
        278: QualifierReference(278, "Tap", "Boolean", "Free kick rolled"),
        279: QualifierReference(279, "Kick off", "Boolean", "Starting pass"),
        280: QualifierReference(280, "Fantasy assist type", "Event ID", "Assist event"),
        281: QualifierReference(281, "Fantasy assisted by", "Text", "Player assist"),
        282: QualifierReference(282, "Fantasy assist team", "Text", "Team assist"),
        283: QualifierReference(283, "Coach ID", "Coach ID", "Team coach ID"),
        284: QualifierReference(284, "Duel", "Boolean", "Blocked shot duel"),
        287: QualifierReference(287, "Over-arm", "Boolean", "Over-arm throw"),
        289: QualifierReference(
            289, "Denied goal-scoring opp", "Boolean", "Denied scoring"
        ),
        290: QualifierReference(290, "Coach types", "Types", "Coach roles"),
    }

    @classmethod
    def get_qualifier_info(cls, qualifier_id: int) -> Optional[QualifierReference]:
        return cls.QUALIFIERS.get(qualifier_id)

    @classmethod
    def get_qualifier_name(cls, qualifier_id: int) -> str:
        qualifier = cls.QUALIFIERS.get(qualifier_id)
        return qualifier.name if qualifier else f"Unknown (ID: {qualifier_id})"

    @classmethod
    def get_qualifier_description(cls, qualifier_id: int) -> str:
        qualifier = cls.QUALIFIERS.get(qualifier_id)
        return qualifier.description if qualifier else "No description"
