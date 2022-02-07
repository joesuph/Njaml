# Not just a markup language

## About 
Njaml (pronounced en-jamol, rhymes with camel and yaml) is a function piping tool that can be implemented for any programming language. It is based on the easy to read and easy to create yaml structure. 

## Why?
This is yet another attempt at a programming framework that is easy to use, easy to skim, easy to verify, and easier to develop software solutions. 

Like YAML, it is hierarchical. In a viewer with collapsing enabled, it is easy to see everything at a high level with the ability to expand sections for as much detail as we want to see.

## Suggested workflow
1. Frame problem as desired input and output
2. Write a short sequence of high-level abstract tasks that would transform the input to output
3. Repeat these 2 steps for each abstract task
4. When a simple implementation is available or a more algorithm heavy section occurs, write an implementation of the task in a executable language.
5. Write the tasks to an .njaml file
6. Load the function structure
7. Link the abstract function name to it's executable language implementation where needed
8. Add test cases
9. Run any function at any level to get results.

## Example

file.njaml
```yaml
outer1
  inner11
    inner111
  inner12
outer2
  inner21
```

example.py
```python
njaml = Njaml()

#Load njaml functions
njaml.load("file.njaml")

njaml.link('inner11',lambda x: x + 2)
njaml.link('inner111',lambda x: x * 2)
njaml.link('inner12',lambda x: x + 2)

njaml.run('outer1',2) # = 10

njaml.run('inner11',2) # = 8

#Add test cases
njaml.set_cases('outer1',[2,3],[10,12])

#run test cases
njaml.run_cases("outer1") # In console: Case 0 passed\n  Case 1 passed\n 2 passed.\n 0 failed.
```
