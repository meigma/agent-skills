# Writing Tutorials

Tutorials are **learning-oriented** documentation where users acquire skills through guided, hands-on experience. A tutorial is a lesson—not a tool for completing tasks.

## Core Principle

> "A tutorial serves the user's acquisition of skills and knowledge—their study."

The goal is building **competence and confidence**, not task completion. Users should finish feeling "I can do this."

## Essential Characteristics

### Learning by Doing
- Users learn through meaningful activities toward achievable goals
- Create experiences that enable learning rather than explaining concepts
- Each step should produce visible, concrete results

### Teacher-Guided
- Implies a relationship between instructor and learner
- The teacher takes responsibility for the student's success
- Use first-person plural: "We will create..." "Let's add..."

### Safe Environment
- Provide a controlled, consequence-free space for learning
- Eliminate unexpected obstacles
- Protect learners from failure that could damage confidence

### Concrete and Particular
- Focus on specific, tangible examples
- Avoid abstractions and generalizations
- Show exactly what to type, click, or do

## Writing Principles

### Show the Destination First
Tell learners where they're going before starting:
```
In this tutorial, we'll build a simple web server that responds
to HTTP requests. By the end, you'll have a working server
running on your machine.
```

### Deliver Frequent Visible Results
Break work into steps that each produce observable output:
```
# Step 3: Test the connection

Run the command:
    $ curl http://localhost:8080

You should see:
    Hello, World!

This confirms our server is responding to requests.
```

### Minimize Explanation
Don't explain why things work—create experiences that demonstrate it:

**Bad (too much explanation):**
```
HTTP uses a request-response model where clients send requests
and servers send responses. The GET method retrieves resources.
Status code 200 indicates success. Now let's make a request...
```

**Good (experiential):**
```
Let's see what our server sends back:
    $ curl -v http://localhost:8080

Notice the "200 OK" in the response—this means success.
```

### Ignore Options and Alternatives
Present ONE path. Don't mention:
- Alternative approaches
- Optional parameters
- Edge cases
- Advanced configurations

Save those for how-to guides and reference documentation.

### Point Out What to Notice
Help learners see cause-and-effect:
```
Look at the terminal where your server is running. You'll see
a new line appeared when we made the request—this is the server
logging each connection.
```

### Provide Exact Expected Output
Show precisely what success looks like:
```
Your directory should now contain these files:
    myproject/
    ├── main.go
    ├── go.mod
    └── handlers/
        └── hello.go
```

## Structure Template

```markdown
# Tutorial: [What the User Will Learn to Do]

Brief description of what we'll build and what skills we'll learn.

## Prerequisites

- List specific requirements
- Link to installation guides (don't explain here)

## What We're Building

Describe the end result. Include a screenshot or diagram if helpful.

## Step 1: [First Action]

Clear instruction for the first step.

    [exact command or code]

Expected result:
    [exact output]

## Step 2: [Second Action]

Continue with next logical step...

[Continue pattern...]

## Step N: Verify It Works

Final verification that everything is working:

    [verification command]

You should see:
    [success output]

## What We Learned

Brief summary of skills acquired:
- Skill 1
- Skill 2
- Skill 3

## Next Steps

Links to:
- Related tutorials for continuing learning
- How-to guides for real-world application
- Explanation for deeper understanding
```

## Quality Checklist

- [ ] Title starts with "Tutorial:" or clearly signals learning
- [ ] Introduction shows what we'll build
- [ ] Prerequisites are specific and linked (not explained)
- [ ] Each step has ONE clear action
- [ ] Every step shows expected output
- [ ] Uses "we" language throughout
- [ ] No unexplained options or alternatives
- [ ] No lengthy conceptual explanations
- [ ] Builds to a working, visible result
- [ ] Links to other doc types for depth (not inline)

## Common Mistakes

### Teaching Too Much
**Problem:** Including extensive explanations of concepts
**Solution:** Link to explanations; let experience teach

### Too Many Choices
**Problem:** "You can use X or Y, depending on..."
**Solution:** Pick one path; mention alternatives in how-to guides

### Assuming Knowledge
**Problem:** "Configure the database connection..."
**Solution:** Show exact steps: "Open `config.yaml` and add these lines..."

### Skipping Verification
**Problem:** Steps without confirmation of success
**Solution:** Every significant step needs visible output

### Breaking Flow
**Problem:** Digressions into related topics
**Solution:** Stay linear; link out for tangents

## The Teacher's Obligation

Tutorials require **perfect reliability**. If a step fails:
- Learner loses confidence in themselves
- Learner loses confidence in the material
- Learning stops

Test every step. Maintain tutorials actively as the product changes.
