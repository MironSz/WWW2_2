function submit_login_form(oFormElement) {
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

function click_logout() {
    document.getElementById("logout").style.display = "none";
    document.getElementById("login").style.display = "block";
    document.getElementById("login_successful").innerHTML = "";

    window.localStorage.removeItem("username");
    window.localStorage.removeItem("password");
    return false;
}


function prepare_crew_table(selector) {
    var xhttp = new XMLHttpRequest();
    var today = new Date();
    var day;
    var month;
    var year;
    if (window.localStorage.getItem("day") == null || window.localStorage.getItem("month") == null ||
        window.localStorage.getItem("year") == null) {
        day = today.getDate();
        month = today.getMonth() + 1; //January is 0!
        year = today.getFullYear();
    } else {
        day = window.localStorage.getItem("day");
        month = window.localStorage.getItem("month");
        year = window.localStorage.getItem("year");
    }

    document.getElementById("excelDataTable").innerHTML = "";

    function prepare_table_from_list(myList) {
        var columns = addAllColumnHeaders(myList, selector);

        for (var i = 0; i < myList.length; i++) {
            var row$ = $('<tr/>');
            for (var colIndex = 0; colIndex < columns.length; colIndex++) {
                var cellValue = myList[i][columns[colIndex]];
                if (cellValue == null)
                    cellValue = "No crew assigned";
                row$.append($('<td/>').html(cellValue));

            }


            $(selector).append(row$);
        }


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
            if (columnSet.length > 0) {
                document.getElementById("crew_div").style.display = "block";
            } else {
                document.getElementById("crew_div").style.display = "none";
            }
            $(selector).append(headerTr$);
            return columnSet;
        }
    }

    xhttp.onreadystatechange = function () {
        var myList = JSON.parse(this.responseText).crews;
        prepare_table_from_list(myList)
    };
    xhttp.open("GET", "/api/flights_and_crews/?day=" + day + "&month=" + month + "&year=" + year, false);
    xhttp.send();
}

function hide_show_login_logout_button() {
    if (window.localStorage.getItem("password") != null && window.localStorage.getItem("username") != null) {
        document.getElementById("login_successful").innerHTML = "You are logged in as " + window.localStorage.getItem("username");
        document.getElementById("logout").style.display = "block";
        document.getElementById("login").style.display = "none";
    }
}

function change_flights_date() {
    var date = document.forms["date_form"]["date_field"].value;
    var year = date.slice(0, 4);
    var month = date.slice(5, 7);
    var day = date.slice(8, 10);
    window.localStorage.setItem("day", day);
    window.localStorage.setItem("month", month);
    window.localStorage.setItem("year", year);
    prepare_crew_table('#excelDataTable');

    return false;
}

function change_crew() {
    var firstname = document.forms["change_crew_form"]["Firstname"].value;
    var surname = document.forms["change_crew_form"]["Surname"].value;
    var flight_id = document.forms["change_crew_form"]["FlightId"].value;
    var username = window.localStorage.getItem("username");
    var password = window.localStorage.getItem("password");
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/api/change_crew/", true);

    xhttp.onreadystatechange = function () {
        var myObj = JSON.parse(this.responseText);
        if (myObj.success === true) {
            document.getElementById("change_error_success").style.display = "none";
            prepare_crew_table("#excelDataTable");
        }
        else {
            document.getElementById("change_error_success").innerHTML = myObj.error;
            document.getElementById("change_error_success").style.display = "block";

        }
    };
    var data = JSON.stringify({
        "password": password, "username": username,
        "flight_id": flight_id, "captain_name": firstname, "captain_surname": surname
    });

    xhttp.send(data);
    return false;
}
