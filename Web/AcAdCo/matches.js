document.addEventListener('DOMContentLoaded', function() {
    let profile = JSON.parse(localStorage.getItem('profile'));
    let matchesContainer = document.getElementById('matches');

    if (profile) {
        let matchesHTML = `
            <h3>Your Profile</h3>
            <p><strong>Name:</strong> ${profile.name}</p>
            <p><strong>Research Interests:</strong> ${profile.researchInterests}</p>
            <p><strong>Experience:</strong> ${profile.experience}</p>
            <p><strong>Projects and Publications:</strong> ${profile.projects}</p>
            <p><strong>Past Conferences Attended:</strong> ${profile.conferences}</p>
            <p><strong>Other Affiliations:</strong> ${profile.affiliations}</p>
            <p><strong>Location Interests:</strong> ${profile.location}</p>
            <p><strong>Seeking:</strong> ${profile.seeking}</p>
        `;
        matchesContainer.innerHTML = matchesHTML;

        // Placeholder for actual matching logic
        matchesContainer.innerHTML += `
            <h3>Matching Advisors</h3>
            <p>No matches found.</p>
            <h3>Matching Collaborators</h3>
            <p>No matches found.</p>
        `;
    } else {
        matchesContainer.innerHTML = '<p>No profile found. Please create a profile first.</p>';
    }
});
