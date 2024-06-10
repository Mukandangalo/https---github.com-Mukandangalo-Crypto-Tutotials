from pyteal import *

# Maximum number of allowed votes
MAX_VOTES = 20

# List of candidates
CANDIDATES = ["Candidate A", "Candidate B", "Candidate C", "Candidate D", "Candidate E"]

def approval_program():
    # Initialize global variables
    on_creation = Seq(
        [
            App.globalPut(Bytes("Creator"), Txn.sender()),
            App.globalPut(Bytes("RegBegin"), Btoi(Txn.application_args[0])),
            App.globalPut(Bytes("RegEnd"), Btoi(Txn.application_args[1])),
            App.globalPut(Bytes("VoteBegin"), Btoi(Txn.application_args[2])),
            App.globalPut(Bytes("VoteEnd"), Btoi(Txn.application_args[3])),
            App.globalPut(Bytes("TotalVotes"), Int(0)),  # Initialize total votes count
            Return(Int(1)),
        ]
    )

    # Check if sender is the creator of the application
    is_creator = Txn.sender() == App.globalGet(Bytes("Creator"))

    # Get the number of votes cast by the sender
    get_vote_of_sender = App.localGetEx(Int(0), App.id(), Txn.sender())

    # Logic to execute on closing out
    on_closeout = Seq(
        [
            get_vote_of_sender,
            If(
                And(
                    Global.round() <= App.globalGet(Bytes("VoteEnd")),
                    get_vote_of_sender.hasValue(),
                ),
                App.globalPut(
                    get_vote_of_sender.value(),
                    App.globalGet(get_vote_of_sender.value()) - Int(1),
                ),
            ),
            Return(Int(1)),
        ]
    )

    # Logic to execute on registration
    on_register = Return(
        And(
            Global.round() >= App.globalGet(Bytes("RegBegin")),
            Global.round() <= App.globalGet(Bytes("RegEnd")),
        ),
    )

    # Logic to execute when voting
    on_vote = Seq(
        [
            Assert(
                And(
                    Global.round() >= App.globalGet(Bytes("VoteBegin")),
                    Global.round() <= App.globalGet(Bytes("VoteEnd")),
                )
            ),
            get_vote_of_sender,
            If(get_vote_of_sender.hasValue(), Return(Int(0))),  # Ensure sender hasn't voted already
            App.globalPut(Bytes("TotalVotes"), App.globalGet(Bytes("TotalVotes")) + Int(1)),  # Increment total votes count
            choice = Txn.application_args[1]

            If(
                choice < Int(0) | choice >= len(CANDIDATES),  # Check if the choice is valid
                Return(Int(0)),
            ),
            App.globalPut(CANDIDATES[choice], App.globalGet(CANDIDATES[choice]) + Int(1)),  # Increment the vote count for the chosen candidate
            App.localPut(Int(0), Txn.sender(), choice),  # Store the vote locally
            Return(Int(1)),
        ]
    )

    program = Cond(
        [Txn.application_id() == Int(0), on_creation],
        [Txn.on_completion() == OnComplete.DeleteApplication, Return(is_creator)],
        [Txn.on_completion() == OnComplete.UpdateApplication, Return(is_creator)],
        [Txn.on_completion() == OnComplete.CloseOut, on_closeout],
        [Txn.on_completion() == OnComplete.OptIn, on_register],
        [Txn.application_args[0] == Bytes("vote"), on_vote],
    )

    return program


def clear_state_program():
    get_vote_of_sender = App.localGetEx(Int(0), App.id(), Txn.sender())
    program = Seq(
        [
            get_vote_of_sender,
            If(
                And(
                    Global.round() <= App.globalGet(Bytes("VoteEnd")),
                    get_vote_of_sender.hasValue(),
                ),
                App.globalPut(
                    get_vote_of_sender.value(),
                    App.globalGet(get_vote_of_sender.value()) - Int(1),
                ),
            ),
            Return(Int(1)),
        ]
    )

    return program


if __name__ == "__main__":
    with open("vote_approval.teal", "w") as f:
        compiled = compileTeal(approval_program(), mode=Mode.Application, version=5)
        f.write(compiled)

    with open("vote_clear_state.teal", "w") as f:
        compiled = compileTeal(clear_state_program(), mode=Mode.Application, version=5)
        f.write(compiled)
