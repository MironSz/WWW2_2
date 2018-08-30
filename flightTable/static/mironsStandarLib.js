function submitLoginForm(oFormElement) {
    var xhttp = new XMLHttpRequest();
    var password = document.forms["login_form"]["password"].value;
    var username = document.forms["login_form"]["username"].value;
    xhttp.onreadystatechange = function () {
        if (this.status === 200) {
            var myObj = JSON.parse(this.responseText);
            if (myObj.success === true) {
                window.localStorage.setItem("api_key", myObj.apiKey);
                window.localStorage.setItem("password", password);
                window.localStorage.setItem("username", username);
                document.getElementById("logout").style.display = "block";
                document.getElementById("login").style.display = "none";
                document.getElementById("login_successful").innerHTML = "You are logged in as " + username;
            } else {
                document.getElementById("login_successful").innerHTML = "Your username or password is incorrect";
            }
        } else {
        }
    };
    xhttp.open("GET", "/api/login_REST/?username=" + username + "&password=" + password, false);
    xhttp.send();
    return false;
}

function submitLogoutForm() {
    document.getElementById("logout").style.display = "none";
    document.getElementById("login").style.display = "block";
    document.getElementById("login_successful").innerHTML = "";

    window.localStorage.removeItem("username");
    window.localStorage.removeItem("password");
    return false;
}


function prepareCrewTable(selector) {
    var xhttp = new XMLHttpRequest();
    var today = new Date();
    var day = today.getDate();
    var month = today.getMonth() + 1; //January is 0!
    var year = today.getFullYear();

    function prepareTableFromList(list){

    }
    xhttp.onreadystatechange = function () {

        var myList = JSON.parse(this.responseText).crews;
        var columns = addAllColumnHeaders(myList, selector);

        for (var i = 0; i < myList.length; i++) {
            var row$ = $('<tr/>');
            for (var colIndex = 0; colIndex < columns.length; colIndex++) {
                var cellValue = myList[i][columns[colIndex]];
                if (cellValue == null) cellValue = "";
                else document.getElementById("debug").innerHTML += cellValue;
                row$.append($('<td/>').html(cellValue));

            }
            row$.append($('<td/>').html("hello"));


            $(selector).append(row$);
        }


        // Adds a header row to the table and returns the set of columns.
        // Need to do union of keys from all records as some records may not contain
        // all records.
        function addAllColumnHeaders(myList, selector) {
            var columnSet = [];
            var headerTr$ = $('<tr/>');

            for (var i = 0; i < myList.length; i++) {
                var rowHash = myList[i];
                for (var key in rowHash) {
                    if ($.inArray(key, columnSet) == -1) {
                        columnSet.push(key);
                        headerTr$.append($('<th/>').html(key));
                    }
                }
            }
            columnSet.push("helloCollumn");
            headerTr$.append($('<th/>').html("helloCollumn"));

            $(selector).append(headerTr$);

            return columnSet;
        }
    }
    xhttp.open("GET", "/api/flights_and_crews/?day=" + day + "&month=" + month + "&year=" + year, false);
    xhttp.send();
}

function hide_show_login_logot_button(){
        if (window.localStorage.getItem("password") != null && window.localStorage.getItem("username") != null) {
        document.getElementById("login_successful").innerHTML = "You are logged in as " + window.localStorage.getItem("username");
        document.getElementById("logout").style.display = "block";
        document.getElementById("login").style.display = "none";
    }
}

function change_flights_date() {
    
}