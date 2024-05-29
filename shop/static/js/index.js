function likePost(postId) {
  const likeCount = document.getElementById(`like-count-${postId}`);
  const likeButton = document.getElementById(`like-btn-${postId}`);
  fetch(`/like/${postId}`, { method: 'POST' })
    .then(response => response.json())
    .then(data => {
      if (data.liked) {
        
        likeButton.innerHTML = '<i class="fa-solid fa-heart"></i>';
      } else {
        
        likeButton.innerHTML = '<i class="fa-regular fa-heart"></i>';
      }
      
      likeCount.innerHTML = data.like_count;
    })
    .catch(error => console.error('Error:', error));
}


$('.plus-cart').click(function(){
  console.log('Button clicked')

  var id = $(this).attr('pid').toString()
  var quantity = this.parentNode.children[2]
  
  $.ajax({
      type: 'GET',
      url: '/pluscart',
      data: {
          cart_id: id
      },
      
      success: function(data){
          console.log(data)
          quantity.innerText = data.quantity
          document.getElementById(`quantity${id}`).innerText = data.quantity
          document.getElementById('amount_tt').innerText = data.amount
          document.getElementById('totalamount').innerText = data.total

      }
  })
})


$('.minus-cart').click(function(){
  console.log('Button clicked');

  var id = $(this).attr('pid').toString();
  var quantityElement = this.parentNode.children[2];
  var currentQuantity = parseInt(quantityElement.innerText);
  
  if (currentQuantity <= 1) {
      console.log('Quantity cannot be less than 1');
      return;
  }

  $.ajax({
      type: 'GET',
      url: '/minuscart',
      data: {
          cart_id: id
      },
      
      success: function(data){
          console.log(data);
          quantityElement.innerText = data.quantity;
          document.getElementById(`quantity${id}`).innerText = data.quantity;
          document.getElementById('amount_tt').innerText = data.amount;
          document.getElementById('totalamount').innerText = data.total;
      }
  });
});





document.addEventListener('DOMContentLoaded', (event) => {
  document.querySelectorAll('[id^="rating-stars-"]').forEach(starContainer => {
      const productId = starContainer.id.split('-')[2];
      const ratingValue = parseFloat(document.getElementById(`rating-value-${productId}`).innerText);
      updateRatingStars(productId, ratingValue);
  });
});

function rateProduct(productId, ratingValue) {
  fetch(`/rate_product/${productId}/${ratingValue}`, {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json',
      }
  })
  .then(response => response.json())
  .then(data => {
      if (data.success) {
          const newRating = parseFloat(data.new_rating).toFixed(1); 
          document.getElementById(`user-rating-value-${productId}`).innerText = `(${ratingValue})`;
          document.getElementById(`rating-value-${productId}`).innerText = newRating;
          updateRatingStars(productId, newRating);
      } else {
          alert(data.message);
      }
  })
  .catch(error => console.error('Error:', error));
}

function updateRatingStars(productId, newRating) {
  const stars = document.querySelectorAll(`#rating-stars-${productId} .star`);
  const wholeStars = Math.floor(newRating);
  const fraction = newRating - wholeStars;
  const hasHalfStar = fraction >= 0.25 && fraction < 0.75;

  stars.forEach((star, index) => {
      if (index < wholeStars) {
          star.innerHTML = '<i class="fa fa-star text-primary"></i>';
      } else if (index === wholeStars && hasHalfStar) {
          star.innerHTML = '<i class="fa fa-star-half-alt text-primary"></i>';
      } else if (index === wholeStars && !hasHalfStar && fraction >= 0.75) {
          star.innerHTML = '<i class="fa fa-star text-primary"></i>';
      } else {
          star.innerHTML = '<i class="fa fa-star text-muted"></i>';
      }
  });
}








