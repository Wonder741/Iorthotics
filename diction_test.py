# Function session_selection choose new session or continue old session
# Inputs pair_count
def initial_session(pair_count):
    sess = input("Start new session? (Enter n for new or any key else for exit)")
    if sess == "n":  # Init new dict
        new_diction = {}
        for pair_position in range(pair_count):
            new_diction[pair_position] = {"location": pair_position, "type": None, "order_number": None,
                                          "pair_found": False, "matched_word": None,
                                          "foot1": {"found_words_pose1": {}, "found_words_pose2": {}},
                                          "foot2": {"found_words_pose1": {}, "found_words_pose2": {}}}
        print("New diction created")
        close_flag = False
    else:
        new_diction = None
        close_flag = True
    return new_diction, close_flag


d = initial_session(20)
print(d)
