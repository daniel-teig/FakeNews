let fs = require('fs')
let python = require('python-shell')


function createTweetBox(tweet) {
    var tweetBox = document.createElement("div")
    tweetBox.className = "tweet-box"

    var wrapper = document.createElement("div")
    wrapper.className = "wrapper"
    tweetBox.appendChild(wrapper)

    var profilePic = document.createElement("div")
    profilePic.className = "profile-pic"

    var image = document.createElement("img")
    image.src = "./pics/" + tweet.user.profilePic
    profilePic.appendChild(image)
    wrapper.appendChild(profilePic)

    var tweetContent = document.createElement("div")
    tweetContent.className = 'tweet-content'
    wrapper.appendChild(tweetContent)

    var userInfoBox = createUserInfoBox(tweet)
    tweetContent.appendChild(userInfoBox)

    var contentDiv = document.createElement("div")
    contentDiv.innerText = tweet.body
    tweetContent.appendChild(contentDiv)

    var tweetInfoBox = createTweetInfoBox(tweet, userInfoBox)
    tweetContent.appendChild(tweetInfoBox)

    return tweetBox
}

function createTweetInfoBox(tweet, userBox) {
    var tweetInfoBox = document.createElement("div")
    tweetInfoBox.className = 'tweet-info-box'
    var commentBox = createButtonBox("./icons/comment.svg", tweet.comments)
    tweetInfoBox.appendChild(commentBox)

    var retweetBox = createButtonBox("./icons/retweet.svg", tweet.retweets)
    tweetInfoBox.appendChild(retweetBox)

    var likeBox = createButtonBox("./icons/heart.svg", tweet.likes)
    tweetInfoBox.appendChild(likeBox)

    var shareBox = createButtonBox("./icons/share.svg", "")
    tweetInfoBox.appendChild(shareBox)



    var reportButton = document.createElement("div")
    reportButton.innerText = '!'
    reportButton.className = "report-button"
    reportButton.onclick = function () {

        var options = {
            scriptPath: "./nlp",
            pythonPath: "/usr/local/bin/python3",
            options: ['-u'],
            args: [`-t ${tweet.body}`]
        }

        let pyshell = new python.PythonShell("checkfact.py", options)
        pyshell.on('message', function (message) {
            // received a message sent from the Python script (a simple "print" statement)
            var checkResult = JSON.parse(message)
            console.log(checkResult)
            tweet = reportTweet(checkResult, tweet)
            var warningBox = markTweet(tweet)
            if (warningBox != null) {
                userBox.appendChild(warningBox)
            }
        });
    }
    var warningBox = markTweet(tweet)
    if (warningBox != null) {
        userBox.appendChild(warningBox)
    }

    tweetInfoBox.appendChild(reportButton)

    return tweetInfoBox

}

function reportTweet(checkResult, tweet) {
    if (checkResult.similarity == 0) {
        return
    } else {

        if (checkResult.fact.fact_type == 1) {
            tweet.reported = "a-true"
        } else {
            tweet.reported = "a-fake"
        }

    }

    return tweet
}


function markTweet(tweet) {

    var warningSign = document.createElement("div")
    warningSign.className = "warning-sign"

    if (tweet.reported == null) {
        return null
    } else if (tweet.reported == "a-true") {
        warningSign.innerHTML = '~'
        warningSign.className += " a-true"
    } else if (tweet.reported == "a-fake") {
        warningSign.innerHTML = 'warning'
        warningSign.className += " a-fake"
    } else if (tweet.reported == "v-true") {
        warningSign.innerHTML = 'verified'
        warningSign.className += " v-true"
    } else if (tweet.reported == "v-fake") {
        warningSign.innerHTML = 'false'
        warningSign.className += " v-fake"
    }

    return warningSign
}



function createButtonBox(iconPath, data) {
    var buttonBox = document.createElement("div")
    buttonBox.className = "button-box"
    var icon = document.createElement("img")
    icon.src = iconPath
    icon.className = 'tweet-icon'
    buttonBox.appendChild(icon)
    buttonBox.innerHTML += data
    return buttonBox
}




function createButtonBox(iconPath, data) {
    var buttonBox = document.createElement("div")
    buttonBox.className = "button-box"
    var icon = document.createElement("img")
    icon.src = iconPath
    icon.className = 'tweet-icon'
    buttonBox.appendChild(icon)
    buttonBox.innerHTML += data

    return buttonBox
}


function createUserInfoBox(tweet) {
    var userInfoBox = document.createElement("div")
    userInfoBox.className = 'user-info-box'

    var nicknameLabel = document.createElement("div")
    nicknameLabel.className = "nickname-label"

    var nicknameLink = document.createElement("a")
    nicknameLink.innerText = tweet.user.nickname
    nicknameLabel.appendChild(nicknameLink)

    var usernameLabel = document.createElement("div")
    var timeLabel = document.createElement("div")
    var timeLink = document.createElement("a")

    usernameLabel.className = "username-label"
    usernameLabel.innerText = tweet.user.username + " ·"
    timeLink.innerText = tweet.postTime
    timeLabel.className = "time-label"
    timeLink.className = "time-label-link"
    timeLabel.appendChild(timeLink)
    userInfoBox.appendChild(nicknameLabel)
    userInfoBox.appendChild(usernameLabel)
    userInfoBox.appendChild(timeLabel)

    return userInfoBox
}


var tweets = JSON.parse(fs.readFileSync('tweets.json', 'utf8'));

var infoBox = document.getElementById('tweet-feed')

for (let i = 0; i < tweets.length; i++) {
    const tweet = tweets[i];
    var tweetBox = createTweetBox(tweet)
    infoBox.appendChild(tweetBox)
}