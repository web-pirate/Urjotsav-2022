// Map your choices to your option value
var lookup = {
   'cultural': [
      'Dance Competition',
      'Singing Compettion',
      'Drama Competition',
      'Fashion Show',
      'Treasure Hunt',
      'Flash Mob',
   ],
   'managerial': [
      'Ad Mad Show',
      'Debate',
      'Logo Making',
      'B-Plan',
      'Case Study',
      'Poster Painting',
   ],
   'sports': [
      'Kabaddi',
      'Kho-Kho',
      'BasketBall',
      'Vollyball',
      'Football',
      'Badmintion',
   ],
   'technical': [
      'Drone Workshop',
      'Circuit Design Competetion',
      'Robot Arm Programming Comp.',
      'Cyber Security Workshop',
      'Areo Modeling Competition',
   ],
   'engineering': [
      'Computer Science Eng.',
      'Mechanical Eng.',
   ],
};

// When an option is changed, search the above for matching choices
$('#options').on('change', function() {
   // Set selected option as variable
   var selectValue = $(this).val();

   // Empty the target field
   $('#choices').empty();
   
   // For each chocie in the selected option
   for (i = 0; i < lookup[selectValue].length; i++) {
      // Output choice in the target field
      $('#choices').append("<option value='" + lookup[selectValue][i] + "'>" + lookup[selectValue][i] + "</option>");
   }
});