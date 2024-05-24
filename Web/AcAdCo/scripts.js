
// submitting fomrs
document.getElementById('profileForm').addEventListener('submit', function(event) {
    event.preventDefault();
  
    let profileData = {
      name: document.getElementById('name').value,
      researchInterests: document.getElementById('researchInterests').value,
      experience: document.getElementById('experience').value,
      projects: document.getElementById('projects').value,
      conferences: document.getElementById('conferences').value,
      affiliations: document.getElementById('affiliations').value,
      location: document.getElementById('location').value,
      seeking: document.getElementById('seeking').value,
    };
  
    localStorage.setItem('profile', JSON.stringify(profileData));
  
    alert('Profile saved successfully!');
  });
  