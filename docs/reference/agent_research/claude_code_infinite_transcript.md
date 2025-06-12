I just broke Claude Code
0:00
engineers I think I just broke Clawude
0:03
Code the best agent coding tool in the
0:05
game check this out and you tell me the
0:08
amount of value you can create in a
0:11
single prompt is incredible the amount
0:13
of value you can create in two prompts
0:16
is insanely mindblowing and not well
0:20
understood let me show you exactly what
0:22
I mean here I'm running a clawed code
0:25
infinite agentic loop now what does that
0:28
mean and what does that look like inside
0:30
of this five directory codebase I'm
0:33
generating infinite self-contained UIs
0:37
that self-improve on each set how is
0:40
this possible if I open up go into
0:43
commands you can see I have this
0:45
infinite.md prompt that's fueling this
0:48
claw code agent that's fired off five
0:51
sub agents you can see them all working
0:53
here live right now this one just wrote
0:56
1,000 lines we have another thousand
0:58
lines here one tool use three one two
1:01
and you can see here this is wave two
1:02
with five agents in parallel and more
1:05
are getting queued up right now you can
1:07
see it just finished wave two how can
1:10
just two prompts make Cloud Code run
1:13
forever you can see wave 3 is getting
1:15
set up right now iterations 16 through
1:18
20 if we scroll down here you can see a
1:20
new set of iterations loaded up check
1:22
out this task list right this is going
1:25
to just keep running back to the
1:28
question how is this possible this is
Infinite Agentic Loop
1:30
enabled by an infinite agentic
1:38
loop this powerful pattern is fueled by
1:41
just two prompts it's fueled by the
1:44
infinite prompt that we're going to get
1:46
into in just a second and of course your
1:48
spec your plan your PRD so if we open
1:51
this up a little bit you can see here I
1:52
have just three specs where we're
1:54
inventing some new UIs i have three
1:56
versions of them let's go ahead and kick
1:58
off another infinite agentic loop like
2:01
this and while it's dedicating work to
2:04
multiple sub agents for us we can talk
2:05
about how you can use this to generate a
2:08
virtually unlimited set of solutions for
2:11
a specific problem i'll create a new
2:13
terminal instance let's fire up cloud
2:15
code here and let's update the model i
2:17
want to fire this off on Opus very
2:20
clearly state-of-the-art model and then
2:22
we'll use the infinite custom slash
2:24
command here i'll type slashinfinite and
2:27
you can see here we have the infinite
2:28
agentic loop command i'll hit tab here
2:31
and now we need to pass in a few
2:33
variables into this so the first
2:35
parameter is the plan we want to fire
2:37
off i'm going to go ahead copy this get
2:39
the path to this paste it in here you
2:42
can see we're still running in the
2:43
background right agent 16 through 20
2:45
still running here it takes a new
2:47
directory so you can see our first agent
2:49
is operating in the source directory
2:50
let's set this directory to
2:53
source_infinite and then lastly it takes
Fire off a new wave of agents
2:56
a count or the information dense keyword
2:59
infinite we're going to of course pass
3:01
in infinite so we're going to kick this
3:03
off and now we're going to have two
3:05
agents running in parallel and so we can
3:08
see here our second infinite agentic
3:11
loop is starting to fire off here so if
3:13
I close this and open up the second
3:15
directory you can see that got created
3:16
here in our plan you can see cloud code
3:19
writing up this plan for infinite
3:21
generation we need to dive into the
3:22
prompt this is the most important thing
3:24
it's the pattern here that's so valuable
3:26
let's go ahead and dive in here and
3:28
understand how this infinite agentic
3:30
loop works with our two prompt system
3:32
and then let's talk about how this
3:33
breaks down if you've been using
3:35
longunning cloud code jobs you already
3:37
know exactly how this breaks there's a
3:40
natural limit here that we're starting
3:41
to bump into over and over and over and
3:44
it completely breaks this infinite
3:46
agentic loop workflow let's start with
3:48
the infinite prompt so we have our
3:49
initial command and then we have a
3:51
really important part of this the
3:53
variables with cloud code custom/comands
3:57
you can pass in arguments like this and
3:59
they'll be placed in position our first
4:01
argument gets replaced with spec and
4:03
then we get infinite source and then we
4:05
get infinite so this gets replaced and
4:07
then we can use these variables
4:09
throughout this prompt and the cloud 4
4:12
series is smart enough to know that it
4:14
should replace the variables we placed
4:16
in here with the actual variables passed
4:19
in right so you can see the spec file
4:20
throughout this prompt and you can see
4:22
the output directory as well then we
4:24
have count which is going to be one to n
4:26
or of course infinite you can see here
4:28
in this first step of the infinite
4:30
agentic loop prompt we're reading the
4:32
spec file this is a really interesting
4:34
pattern we're treating prompts right our
4:37
specs as first class citizens that can
4:40
be passed in to other prompts okay this
4:44
is a really powerful technique there's a
4:46
lot of value here that's untapped we
4:48
explored this a little bit in our
4:50
parallel agent decoding with git work
4:52
trees video we put out a couple weeks
4:54
ago what we're doing here is a little
4:56
different because we're running
4:57
infinitely and we're generating a single
5:00
file although to be completely clear you
5:02
know we could rewrite this prompt to
5:04
generate any set of files so we have
5:06
argument parsing our agent is going to
5:08
first read the spec file to understand
5:10
what's going on then it's going to
5:12
understand where it's going to output
5:13
all these files then it's going to fire
5:16
off parallel agents in groups of five
5:19
this is going to speed up the output of
5:21
our agent our first round files have
5:23
already been created for that infinite
5:24
loop and then this is really important
5:26
we're actually specifying what each sub
5:28
aent receives okay okay so it's getting
5:30
the spec it's getting the directory it's
5:33
getting its iteration number right you
5:35
can see they all have their own
5:36
iteration number and it's getting their
5:38
uniqueness directive right we want these
5:40
all to be unique we want each example to
5:42
grow on each other this is really cool
5:43
so here we're actually passing in a
5:46
prompt for our sub aents so that's
5:49
what's getting written out here right
5:50
this is a concise prompt for the sub
5:52
aent and then we have you know phase
5:54
five we're just kind of continuing down
5:55
the line infinite cycle and then I have
5:58
this line in here i'm not 100% sure if
6:00
this works i don't know if Claude can
6:02
see the end of its context window but it
6:04
seems to work okay evaluate context
6:06
capacity remaining if sufficient
6:08
continue with next wave if approaching
6:10
limits complete and finalize right so
6:12
this is where this pattern completely
6:13
breaks clog code you can't keep running
6:15
this it's going to hit the context
6:17
window of course we don't actually have
6:19
infinite context windows this will
6:21
generate you know some 20 30 files or
6:24
sets um depending on your setup all
6:27
right all right so then we're going to
6:28
just continue along the lines here there
6:29
are some details at the bottom here not
6:31
all this matters as you can see here I
6:33
am writing these prompts now with agents
6:36
we're entering this interesting zone
6:38
where you want to be writing prompts
6:39
that write the prompts for you you can
6:41
see here you know both of our lists here
6:43
are continuing to expand we now have 10
6:45
hybrid UIs inside of Source Infinite
6:48
let's go ahead and actually look at what
6:49
the heck is getting generated here right
6:51
you know just to briefly describe the
6:53
prompt that we're passing in right so we
6:56
have our spec file that we're passing in
6:59
to our infinite agentic loop prompt
7:02
we're saying invent new UI v3 and what
7:05
we're doing here is we're creating
7:06
uniquely themed UI components that
7:08
combines multiple existing UIs into one
7:11
elegant solution okay and that's that's
7:13
basically it that's a key idea of what
7:14
we're doing here and I'm using UI as a
7:17
example just like with our parallel
7:19
agent decoding video with git work trees
7:22
ui is just the simplest way to show off
7:23
a powerful pattern like this you know
7:25
we're specifying that naming scheme here
7:27
with the iteration and then we have a
7:29
kind of rough HTML structure that's all
Reviewing the Claude 4 Opus UIs
7:31
self-contained into a single file so
7:32
let's go and open this up let's see what
7:34
this looks like right so if we open up a
7:36
terminal here and we get the path to one
7:38
of these files we can say uh Chrome and
7:41
then open up one of these files check
7:42
this out neural implant
7:45
registry um very interesting this is a
7:48
classified database access terminal very
7:51
clearly it's just a table right so this
7:52
is kind of interesting it's got a really
7:54
cool unique theme to it let's see what
7:56
we can do here so we can search nice
7:59
echo cerebra max okay great so we can
8:02
search across columns we can sort that
8:05
looks great status filters active risk
8:07
level here i'm constantly impressed with
8:10
the caliber of code that the Cloud 4
8:13
series is producing now it's just kind
8:15
of mind-blowing that not only was it
8:17
able to launch off this it did five
8:19
versions at the same time right you and
8:22
I we really have access to premium
8:24
compute that we can now scale up
8:26
infinitely uh with this pattern right
8:29
very cool UI let's go on to another
8:31
example right adaptive flow UI liquid
8:33
metal so obviously some UI issues here
8:36
but this is just a simple UI it looks
8:38
like nothing special oh interesting that
8:40
just adapted very interesting i did not
8:42
expect that so it's actually creating
8:45
additional UI here based on what we type
8:48
in oh I like this kind of error state
8:50
look at this it's errored right here
8:52
right this is not a true email address
8:54
and we do get email autocomplete here
8:56
very cool and you can see we also have a
8:57
progress bar here at the bottom in
8:59
particular I like this like active state
9:01
let's go ahead and look at another UI
9:03
that was generated for us again this is
9:05
all happening in parallel in the
9:06
background you know this compute is
9:08
solving this problem for us at scale
9:11
creating many many versions right what
9:13
do we have some 20 um yeah 50 versions
9:17
now with two parallel infinite agenda
9:20
coding agents this is crazy right this
9:21
it's really cool very powerful obviously
9:24
the real trick with this pattern is
9:26
going to be to pointing it at a problem
9:28
where you need multiple potential
9:30
solutions okay this is the real trick
9:32
with this pattern you know everything we
9:33
do on the channel you need to take it
9:35
and you need to point it at a problem
9:37
there's a ton of value here that you can
9:40
get out of this interesting interesting
9:42
twoprompt infinite agentic loop pattern
9:45
right we're starting to compose prompts
9:48
we already know that great planning is
9:49
great prompting and you know maybe
9:51
that's a important thing to really
9:52
highlight here right we're generating
9:54
all these cool UIs um you know we can
9:56
continue to just look at look look at
9:58
this so interesting right we can look at
9:59
UI after
10:01
UI right after UI and look at this one
10:06
so interesting right look at all these
10:08
just interesting creative UIs there's
10:10
you know a lot of likely garbage here
10:12
but there's a lot of value here as well
10:14
right we're literally inventing new UIs
10:17
as we go along and new UI patterns right
10:19
we can just keep going check this one
10:21
out how cool is this okay so you know
10:24
this is the power of an infinite agentic
10:26
loop multiple solutions it's just going
10:28
to keep going keep firing we're using a
10:31
ton and ton and ton of compute here
10:34
right you can see we're launching
10:35
another wave of agents inside of this
10:38
agent right one tool call 30k 30k 30k 2
10:42
minutes each these are shorter jobs i've
10:45
run jobs that are 30 minutes plus and
10:48
you can fire them all off in a subtask
10:50
it's so incredible what we can do with
10:51
cloud code and with the right pattern
10:54
right the right prompting patterns that
10:56
lets us scale compute okay so really
10:58
interesting stuff there what's important
11:00
what's the signal here right couple
11:02
things to call out um you can pass
11:05
prompts into prompts you can specify
11:08
variables at the top of your files
11:11
you're likely going to want multiple
11:12
variables that control what happens and
11:15
what gets done okay we have this
11:18
infinite information dense keyword this
11:21
triggers our agenda coding tool to run
11:23
infinitely of course you need to phrase
11:25
things you need to be more specific with
11:27
how that works you can start with this
Great Planning is Great Prompting
11:30
prompt and modify it build it make it
11:32
your own couple more key ideas this is a
11:34
classic one right um we have been using
11:37
plans for over a year now on the channel
11:40
and every principal AI coding member you
11:43
know that great planning is great
11:44
prompting i sound like a broken record
11:47
bringing this up for you know over half
11:49
a year now but there's a reason for it
11:51
okay we know that tools will change we
11:53
know that models will improve you can't
11:54
fixate on these things right cloud code
11:57
is the very clear winner right now but
12:00
it won't always be that way okay and
12:02
we're going to get another model all
12:03
that stuff changes what doesn't change
12:05
is the principles of AI coding many of
12:07
you know this is why I built principled
12:09
AI coding sorry for existing members and
12:12
for engineers that have already taken
12:13
this but the repetition is probably
12:15
important anyway it's so so important to
12:17
realize that you want foundational
12:19
skills that don't change with the next
12:22
model with the next tool the plan right
12:25
great planning is great prompting this
12:27
is principle four or five this is so
12:29
relevant it's increasingly important
12:32
okay why is that it's because we can now
12:34
scale or compute further right but how
12:36
we do that is always about communicating
12:40
to our agents okay cloud code is the
12:42
best top agent right now for engineering
12:45
why is that it's because it operates in
12:47
the highest leverage environment for
12:49
engineers the terminal anything you can
12:52
do claw code can do and you know part of
12:55
me wants to say better you know we'll
12:57
debate that more in the channel as time
12:59
goes on it's definitely getting there uh
13:00
but you can see we're generating yet
13:02
another batch of agents here okay we
13:04
have this ocean file explorer very
13:06
interesting but anyways refocusing here
13:08
right the spec is super important
13:10
because this details what we want done
13:12
inside of this infinite agentic loop
13:15
right so we have this really cool
13:16
pattern where we're treating our prompts
13:19
like you can treat functions in certain
13:21
languages right you can you can pass the
13:23
function into a function that's what
13:25
we're doing here right the same idea
13:27
transferred to this domain of agentic
13:30
coding and really prompt engineering
13:31
we're taking a prompt passing it in to a
13:34
prompt you know the magic is obviously
13:36
in the pattern of this infinite agentic
13:38
loop but it's really in what you ask
13:41
your spec to do right it's what you ask
13:43
your agent to do there's a ton and ton
13:46
of value in this pattern i hope you can
13:48
see how powerful this is when do you
13:51
want to use something like this look at
13:53
all these UIs we have generating right
13:54
we have two two uh agents going back to
13:57
back
13:58
here very very cool so what when do you
14:01
want to use something like this you want
14:02
to use a pattern like this it's very
14:04
similar again to our parallel agent
14:07
coding with git work trees there we
14:09
cloned our entire codebase into the work
14:11
tree directory so that multiple agents
14:13
can work on their own directories again
14:15
link for that video is going to be in
14:16
the description i highly recommend you
14:17
check that out but what we're doing here
14:19
is so fascinating it's so powerful we're
14:21
scaling our compute we're solving a
14:23
specific problem with many variations of
14:26
how it can be solved so when do you want
14:28
to use the infinite agentic loop you
14:30
want to use it when there are multiple
14:32
potential solutions that you want to
14:34
explore you want to use it when you're
14:35
working on a hard problem that you don't
14:37
know the answer to and you think that
14:39
having many versions will help you get
When to use the Infinite Agentic Loop
14:41
closer and so this is all stuff you
14:43
would encode in your lower level prompt
14:45
that the infinite agentic loop prompt
14:47
will execute on right and you want to
14:49
use this when this is a really really
14:51
big idea uh this is like a lead
14:54
researchers are doing this when you want
14:55
to set up a self-improving agentic
14:58
workflow that is trying to achieve some
15:02
verifiable outcome that increases over
15:05
time okay we've all heard about
15:07
reinforcement learning you can take that
15:09
idea of reinforcement learning you can
15:10
take that idea of self-verifiable
15:12
domains and you can embed it in an
15:14
infinite agentic loop prompt like this
15:17
uh this is a really really big idea more
15:19
on this on the channel in the future we
15:21
don't have enough time to cover that
15:23
here right now but that's just really
15:24
important to call out those are kind of
15:26
the three big use cases for this that I
15:28
can find right away i'm sure if you dig
15:30
into this if you start using this you'll
15:32
find uh more you know use cases for this
15:34
right so pretty incredible stuff right
15:36
we have two agents running in cloud code
15:38
you can see I am hitting the limit i'm
15:40
breaking cloud code right now okay we're
15:42
running just straight out of Opus
15:44
credits i am running in the cloud code
15:46
max pro subscription wherever the top
15:48
tier is i'm going to go ahead i'm going
15:49
to stop these agents i I need a few more
15:51
credits for today to um do some other
15:54
engineering work i'm going to stop these
15:55
here you can see we're literally
15:57
infinitely generating tons and tons of
16:01
solutions to this problem right that's
16:03
the trick here right that's the real
16:05
value prop of the infinite agentic loop
16:07
you want multiple versions multiple
16:09
potential futures of an answer to a
16:11
problem that you have okay ui is
16:13
obviously just the simplest one that's
16:14
why I've showed it here a couple times
16:15
on the channel um you know we can just
16:17
keep looking through these different
16:19
user interfaces with different ideas and
16:21
themes blended together check this one
16:23
out very smooth very cool um and this is
16:26
all happening you know in the background
16:28
with compute we're scaling up doing this
16:30
again we're scaling up our compute even
16:33
further beyond that's what we do on the
16:35
channel every single Monday check out
16:37
Principal AI coding as many of you know
16:38
I am actively working on the second
16:41
phase course this is the foundation i
16:44
highly recommend you check this out what
16:45
comes next after AI coding is of course
16:48
agentic coding i'll have more details on
16:51
the next generation course as we move
16:53
closer to the release date looking at a
16:55
Q3 launch so stay tuned for that you
16:57
know this is a really powerful technique
16:58
try this don't ignore this please uh for
17:01
your own good um you know it's
17:02
completely free a lot of the stuff I'm
17:04
doing here obviously is all free for you
17:06
guys link in the description to this
17:07
codebase i'll save some of these
17:09
generations so you can kind of really
17:11
see and understand how this works but
17:13
it's really about the infinite prompt
17:15
take all this stuff make it your own
17:17
improve on it solve your problem better
17:19
than ever with compute big theme on the
17:21
channel to scale your impact you scale
17:23
your compute okay tune in make sure you
17:26
subscribe like all that good stuff
17:28
compute equals success scale your
17:30
compute you win you know where to find
17:32
me every single Monday stay focused and
17:35
keep building