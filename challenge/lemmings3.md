The game Lemmings involves critters with fairly simple brains. So simple that we are going to model it using a finite state machine.
In the Lemmings' 2D world, Lemmings can be in one of two states: walking left or walking right. It will switch directions if it hits an obstacle. In particular, if a Lemming is bumped on the left, it will walk right. If it's bumped on the right, it will walk left. If it's bumped on both sides at the same time, it will still switch directions.
In addition to walking left and right, Lemmings will fall (and presumably go "aaah!") if the ground disappears underneath them.
In addition to walking left and right and changing direction when bumped, when ground=0, the Lemming will fall and say "aaah!". When the ground reappears (ground=1), the Lemming will resume walking in the same direction as before the fall. Being bumped while falling does not affect the walking direction, and being bumped in the same cycle as ground disappears (but not yet falling), or when the ground reappears while still falling, also does not affect the walking direction.
In addition to walking and falling, Lemmings can sometimes be told to do useful things, like dig (it starts digging when dig=1). A Lemming can dig if it is currently walking on ground (ground=1 and not falling), and will continue digging until it reaches the other side (ground=0). At that point, since there is no ground, it will fall (aaah!), then continue walking in its original direction once it hits ground again. As with falling, being bumped while digging has no effect, and being told to dig when falling or when there is no ground is ignored.
(In other words, a walking Lemming can fall, dig, or switch directions. If more than one of these conditions are satisfied, fall has higher precedence than dig, which has higher precedence than switching directions.)
Build a finite state machine to model this behaviour.

module dut(
    input clk,
    input areset,    // Freshly brainwashed Lemmings walk left.
    input bump_left,
    input bump_right,
    input ground,
    input dig,
    output walk_left,
    output walk_right,
    output aaah,
    output digging );

I'll will demonstrate behavier of Lemmings in the following table:
| cycle | bump_left | bump_right | ground | dig || walk_left | walk_right | aaah | digging |
| --- | --- | --- | --- | --- || --- | --- | --- | --- |
| 0 | 0 | 0 | 1 | 0 || 1 | 0 | 0 | 0 |
| 1 | 0 | 0 | 1 | 0 || 1 | 0 | 0 | 0 |
| 2 | 0 | 0 | 1 | 1 || 1 | 0 | 0 | 0 |
| 3 | 0 | 0 | 1 | 0 || 0 | 0 | 0 | 1 |
| 4 | 1 | 0 | 1 | 0 || 0 | 0 | 0 | 1 (bump will be ignored when digging) |
| 5 | 0 | 0 | 1 | 0 || 0 | 0 | 0 | 1 |
| 6 | 0 | 0 | 0 | 0 || 0 | 0 | 0 | 1 (digging will stop when no ground)|
| 7 | 0 | 0 | 0 | 0 || 0 | 0 | 1 | 0 |
| 8 | 0 | 0 | 0 | 0 || 0 | 0 | 1 | 0 |
| 9 | 0 | 0 | 1 | 1 || 0 | 0 | 1 | 0 (dig is ignored when falling) |
| 10 | 0 | 0 | 1 | 0 || 1 | 0 | 0 | 0 |
| 11 | 0 | 0 | 1 | 0 || 1 | 0 | 0 | 0 |


* 请特别注意操作之间的优先级
  
* 输入和当前状态决定下一状态，而输出只取决于当前状态