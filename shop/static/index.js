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
  console.log('Button clicked')

  var id = $(this).attr('pid').toString()
  var quantity = this.parentNode.children[2]

  $.ajax({
      type: 'GET',
      url: '/minuscart',
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

