# Code Judge

The `code_judge` web application is a platform designed to facilitate coding challenges.
still in nascent stage, Below are the features available in the current version of the app

## Features

### Authentication System

- Implemented using Django’s native authentication system.
- Provides user login, registration, and authentication functionalities.

### Problem Bank

- Displays the list of coding problems available for users to solve (go through for now).

### Problem Details Page

- Provides detailed information about a specific problem, including its description and requirements.

### Recommendation System

- Suggests coding problems to users based on their skill level and past activities.
    - the system give 60% weight on problem with similar tags
    - the rest 40% on embedding similarity of problem discription of last problems
    - both get on with similar difficulties to the couple of previous problems 
- Helps users discover problem tailored to their then interests.

### chatspace
- 2 friends can collobrate on solving a problem, taking learning to a collobrative effort than solo grind 