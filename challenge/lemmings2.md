The game Lemmings involves critters with fairly simple brains. So simple that we are going to model it using a finite state machine.
In the Lemmings' 2D world, Lemmings can be in one of two states: walking left or walking right. It will switch directions if it hits an obstacle. In particular, if a Lemming is bumped on the left, it will walk right. If it's bumped on the right, it will walk left. If it's bumped on both sides at the same time, it will still switch directions.
In addition to walking left and right, Lemmings will fall (and presumably go "aaah!") if the ground disappears underneath them.
In addition to walking left and right and changing direction when bumped, when ground=0, the Lemming will fall and say "aaah!". When the ground reappears (ground=1), the Lemming will resume walking in the same direction as before the fall. Being bumped while falling does not affect the walking direction, and being bumped in the same cycle as ground disappears (but not yet falling), or when the ground reappears while still falling, also does not affect the walking direction.
Build a finite state machine that models this behaviour.

Module Declaration
module dut(
    input clk,
    input areset,    // Freshly brainwashed Lemmings walk left.
    input bump_left,
    input bump_right,
    input ground,
    output walk_left,
    output walk_right,
    output aaah ); 

* 请特别注意操作之间的优先级
  
* 输入和当前状态决定下一状态，而输出只取决于当前状态