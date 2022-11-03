Events.SequenceGameInitComplete.Add(
function()
    print("Game init is complete. Starting automation");
	Events.LoadScreenClose();
	Game.SetPausePlayer( -1 );
	Game.SetAIAutoPlay(1,-1);
end );
