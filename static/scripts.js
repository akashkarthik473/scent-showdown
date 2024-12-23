function updateImage(option) {
    $.get("/random_image", function(data) {
        $("#" + option + "-img").attr("src", "https://fimgs.net/mdimg/perfume/375x500." + data.image_id + ".jpg");
    });
}

function saveVote(option) {
    // Ensure URL splitting logic is robust
    const src = $("#" + option + "-img").attr("src");
    const imageId = src.match(/375x500\.(\d+)\.jpg/)[1]; // Extract ID using regex
    console.log("Parsed image_id:", imageId);  // Debug parsed image ID

    $.ajax({
        url: "/save_vote",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify({ image_id: imageId }),
        success: function(response) {
            console.log("Vote saved:", response.message);
            updateImage(option); // Update image after vote
            fetchResults(); // Refresh results
        },
        error: function(jqXHR) {
            console.error("Failed to save vote:", jqXHR.responseText);
            alert("Failed to save your vote. Error: " + jqXHR.responseText);
        },
    });
}



function fetchResults() {
    $.get("/get_results", function(data) {
        let resultsHTML = "<h2>Poll Results</h2><div class='grid-container'>";
        data.forEach(result => {
            resultsHTML += `
                <div class="grid-item">
                    <img id="option${result.image_id}-img"
                         src="https://fimgs.net/mdimg/perfume/375x500.${result.image_id}.jpg"
                         alt="Option ${result.image_id} Image"
                         class="custom-img2">
                    <p>${result.votes} votes</p>
                </div>`;
        });
        resultsHTML += "</div>";
        $("#results").html(resultsHTML);
    });
}




$("#option1-btn").click(function() {
    saveVote("option1");
});

$("#option2-btn").click(function() {
    saveVote("option2");
});
