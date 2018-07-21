
var opaque_background = document.querySelector("#opaque-background");

var todo_list = document.querySelector("#todolist");
var incomplete_section = todo_list.querySelector("#incomplete");
var complete_section = todo_list.querySelector("#complete");

var submission_form = document.querySelector("#submission-form");

var completed_toggle = document.querySelector("#completed-toggle");

completed_toggle.addEventListener("click", function() {
    var display = complete_section.style.display;
    if (display == "block") {
        complete_section.style.display = "none";
    }
    else {
        complete_section.style.display = "block";
    }
});

function displayDetails(todo) {
    var input_fields = submission_form.getElementsByClassName("input");
    for (var i = 0; i < input_fields.length; i++) {
        var input_field = input_fields[i];
        var field_type = input_field.type;
        var field_id = input_field.name;
        
        if (field_type != "radio") {
        input_field.value = todo[field_id];  
        }
        else {
            if (todo[field_id] == input_field.value) {
                input_field.checked = true;
            }
        }
    }
}

function displayTODOList(todos, item_created) {

    todos.forEach(function (todo) {
        var todo_item = document.createElement("div");
        var todo_title = document.createElement("div");
        var complete_button = document.createElement("div");
        var delete_button = document.createElement("div");
        var clear = document.createElement("div");
        var save_button = document.createElement("button");

        todo_item.className = "todo-item";
        todo_title.className = "todo-title";
        complete_button.className = "complete-button";
        delete_button.className = "delete-button";
        clear.className = "clear";
        
        complete_button.title = "Complete";
        delete_button.title = "Delete";


        var save_container = document.querySelector("#save-container");
        todo_title.innerHTML = todo["short_description"];
        todo_title.addEventListener("click", function() {
            save_container.innerHTML = "";
            save_container.appendChild(save_button);
            submission_form.style.display = "block";
            displayDetails(todo);
        });

        todo_item.appendChild(complete_button);
        todo_item.appendChild(todo_title);
        todo_item.appendChild(delete_button);
        todo_item.appendChild(clear);

        if (todo["completion_status"] == "incomplete") {
            incomplete_section.appendChild(todo_item);
        }
        else {
            complete_section.appendChild(todo_item);
            todo_item.removeChild(complete_button);
        }

        delete_button.addEventListener("click", function() {
            if (confirm("Please confirm item deletion.")) {
                clearFormValues();
                deleteTODO(todo["rowid"]);
                try {
                    incomplete_section.removeChild(todo_item);
                }
                catch(err) {
                    complete_section.removeChild(todo_item);
                }
            }
        });

        complete_button.addEventListener("click", function() {
            var query_string = createCompletionString(todo);
            replaceTODO(todo["rowid"], query_string);            
        });


        save_button.id = "save-button";
        save_button.innerHTML = "Save";
        save_button.className = "input-button";
        save_button.addEventListener("click", function() {
            var encoded_string = grabFormValues();
            replaceTODO(todo["rowid"], encoded_string);
        });

    });


    var clear = document.createElement("div");
    clear.className = "clear";
    var creation_wrapper = document.createElement("div");
    creation_wrapper.id = "creation-wrapper";

    var create_button = document.createElement("div");
    create_button.id = "create-button";
    create_button.title = "Create";

    var title_input = document.createElement("div");
    title_input.id = "title-input";
    title_input.contentEditable = "true";

    create_button.addEventListener("click", function() {
        var title = title_input.innerHTML;
        if (title) {
            clearFormValues();
            createTODO(title);
        }
    });
    title_input.addEventListener("keypress", function(event) {
        if (event.keyCode == 13) {
            create_button.click();
        }
    });

    creation_wrapper.appendChild(create_button);
    creation_wrapper.appendChild(title_input);
    creation_wrapper.appendChild(clear);
    incomplete_section.appendChild(creation_wrapper);



    if (item_created) {
        var incomplete_items = incomplete_section.getElementsByClassName("todo-item");
        var last_todo = incomplete_items[incomplete_items.length-1].querySelector(".todo-title");
        last_todo.click();
    }
    
    todo_list.style.display = "block";
}

function displayAuth() {
    opaque_background.style.display = "block";
    log_reg_div.style.display = "block";
    log_form.style.display = "block";
}

function grabFormValues() {
    encoded_body = "";
    var input_fields = submission_form.getElementsByClassName("input");
    for (var i = 0; i < input_fields.length; i++) {
        var input_field = input_fields[i];
        var type = input_field.type;
        if (type != "radio") {
            var key = input_field.name;
            var value = input_field.value;
            if (!value) {
                value = " ";
            }
            var encoded_pair = key + "=" + encodeURIComponent(value);
            encoded_body += encoded_pair + "&";
        }
        else {
            if (input_field.checked) {
                var key = input_field.name;
                var value = input_field.value;
                if (!value) {
                    value = " ";
                }
                var encoded_pair = key + "=" + encodeURIComponent(value);
                encoded_body += (encoded_pair + "&");
            }
        }
    }
    
    return encoded_body.slice(0,-1);
}

function clearFormValues() {
    var input_fields = submission_form.getElementsByClassName("input");
    for (var i = 0; i < input_fields.length; i++) {
        var input_field = input_fields[i];
        var type = input_field.type;
        if (type != "radio") {
            input_field.value = "";
        }
        else {
            input_field.checked = false;
        }
    }
}

function createCompletionString(todo) {
    var query_string = "";
    for (key in todo) {
        var query_value = todo[key];
        if (key == "completion_status") {
            query_value = "complete";
        }
        query_string += (key + '=' + query_value + '&');
    }
    return query_string.slice(0,-1);
}


// TODO Ajax requests

var authorized = false;
function listTODOs(item_created) {
    complete_section.innerHTML = "";
    incomplete_section.innerHTML = "";
    
    fetch('http://localhost:8080/todos', {credentials: 'include'} ).then(function(response) {
        if (response.status == 200) {
            authorized = true;
        }
        else {
            displayAuth();
        }
        return response.json();
    }).then(function(todos) {
        if (authorized) {
            displayTODOList(todos, item_created);
        }

    });

}

function retrieveTODO(ID) {
    fetch('http://localhost:8080/todos/' + ID.toString(), {credentials: 'include'} ).then(function(response) {
        return response.json();
    });
}

function createTODO(title) {
    var currentDate = new Date();
    var month = currentDate.getMonth() + 1;
    var day = currentDate.getDate();
    var year = currentDate.getFullYear();
    var date_entered = year + '-' + month + '-' + day;
    var default_todo = "short_description= " + title + "&long_description= &priority=1&desired_completion_date= &due_date= &completion_status=incomplete&date_entered=" + date_entered;

    fetch('http://localhost:8080/todos', {
        method: 'POST',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: default_todo
    }).then(function() {
        incomplete_section.innerHTML = "";
        complete_section.innerHTML = "";
        listTODOs(true);
    });
}

function replaceTODO(ID, encoded_string) {
    fetch('http://localhost:8080/todos/' + ID.toString(), {
        method: 'PUT',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: encoded_string
    }).then(function() {
        listTODOs();
    });
}

function deleteTODO(ID) {
    fetch('http://localhost:8080/todos/' + ID.toString(), {
        method: 'DELETE',
        credentials: 'include',
    });
}


// Registration and Authentication

var log_reg_div = document.querySelector("#login-register");

var log_display_btn = document.querySelector("#log-display-btn");
var log_form = document.querySelector("#log-form");
var reg_display_btn = document.querySelector("#reg-display-btn");
var reg_form = document.querySelector("#reg-form");

var log_error = document.querySelector("#log-error");
var reg_error = document.querySelector("#reg-error");

var account_created = document.querySelector("#account-created");
var login_title = document.querySelector("#login-title");

var welcome = document.querySelector("#welcome");

var log_button = document.querySelector("#log-button");
var reg_button = document.querySelector("#reg-button");

var log_password_field = document.querySelector("#log-password");

log_display_btn.addEventListener("click", function() {
    log_error.innerHTML = "";
    clearAuthForms("sessions");
    reg_form.style.display = "none";
    log_form.style.display = "block";
});
reg_display_btn.addEventListener("click", function() {
    log_form.style.display = "none";
    reg_form.style.display = "block";
});


log_button.addEventListener("click", function() {
    createAuth("sessions");
    clearAuthForms("sessions");
});
reg_button.addEventListener("click", function() {
    createAuth("users");
});

log_password_field.addEventListener("keypress", function(event) {
    if (event.keyCode == 13) {
        log_button.click();
        clearAuthForms("sessions");
    }
});


function createAuth(userOrSession) {

    var query_string = getAuthQueryString(userOrSession);
    
    fetch('http://localhost:8080/' + userOrSession, {
        method: 'POST',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: query_string
    }).then(function(response) {
        if (response.status == 401) {
            log_error.innerHTML = "Invalid email or password.";
        }
        else if (response.status == 422) {
            reg_error.innerHTML = "Email already taken.";
        } 
        else if (response.status == 201) {
            if (userOrSession == "sessions") {
                log_reg_div.style.display = "none";
                opaque_background.style.display = "none";
                log_form.style.display = "none";
                account_created.innerHTML = "";
                listTODOs(false);
            }
            else if (userOrSession == "users") {
                reg_display_btn.style.display = "none";
                reg_form.style.display = "none";
                log_form.style.display = "block";
                account_created.innerHTML = "Account Created";
                login_title.innerHTML = "Please, Login.";
            }
        }
        return response.json();
    }).then(function(data) {
        if (userOrSession == "sessions") {
            var fname = data[0]["fname"];
            welcome.innerHTML = "<h2>Welcome " + fname + "." + "</h2>";
            welcome.style.display = "block";
        }
    });
}

function getAuthQueryString(userOrSession) {
    var query_string = "";
    if (userOrSession == "users") {
        var input_list = reg_form.getElementsByTagName("input");
    }
    else if (userOrSession == "sessions") {
        var input_list = log_form.getElementsByTagName("input");
    }
    for (var i = 0; i < input_list.length; i++) {
        var input_name = input_list[i].name;
        var input_value = input_list[i].value;
        query_string += (input_name + "=" + input_value + "&");
    }
    query_string = query_string.slice(0, -1);
    return query_string;
}


function clearAuthForms(userOrSession) {
    if (userOrSession == "users") {
        var input_list = reg_form.getElementsByTagName("input");
    }
    else if (userOrSession == "sessions") {
        var input_list = log_form.getElementsByTagName("input");
    }
    var input_list = log_form.getElementsByTagName("input");
    for (var i = 0; i < input_list.length; i++) {
        var input_value = input_list[i].value = "";
    }
}


function onPageLoad() {
    listTODOs(false);
}
onPageLoad();



