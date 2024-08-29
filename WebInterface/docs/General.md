# General


## Todo:
- [ ] Figure out universal Styling/structure
- [X] Frontend Auth
- [ ] Config file?  
        - config class
- [X] Fix up command_console
- [ ] Document all of the:
    - Endpoints
    - Relative logic
    - User Docs?
    - Other?

- [X] Clients list (need to do some server work for that one)
    /clients exists now, just need to set it up client side and parse that data now
- [X] Include JWT in requests

- [ ] CLenaup/robustify
    - [ ] consitent names to align w server (token needs to be access_token)

- [ ] Nice to haves:
    - [ ] Dropdown/list of previously connected servers on login


- [ ] command_console
    - [ ] Accurate connection menu/if connected
        - server status/connection/ping 

- [ ] 401 error
    - [X]basically, if 401, use creds, re-login
        function done, haven't run itno the bug since tho. weird. its there if needed
    Add logout button too


- [ ] formj
    - [ ] Docs on key constructor/whole process
    - [ ] move key constructor to api as well if needed.
    - [ ] logging key constructor

- Left off doing cleanup + making it pretty
 
    - [X] need a universal color scheme
        - [X] grey buttons to match anything?

    - [ ] Mock client rev shell wokrs. Just clean up everything around it. no more adding till
    that's done + merged
        - [X] all 3 keys need to work/be constucted properly
            - something to think abuot, making some of the keys NOT list based, as it doesn;t make a ton of sense for somethgn like sleep.
        - [X] Audit log needs to wrok (server side)
            - fixed, had it disabled from testing
        - [ ] Fail test the gui/werid circumstances
        - [X] Get rid of color switch on login
        - [ ] aggrid auto sort by latest client?

## Structure

Each module can be a class or a set of fucntions, whatever works best. 

## Tailwind CSS Docs for ref:

https://tailwindcss.com/docs/flex
