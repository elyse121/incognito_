// Sample data
    const postsData = [
      {
        id: 1,
        author: {
          name: "John Doe",
          avatar: "https://i.pravatar.cc/150?img=5"
        },
        content: "Check out this amazing new feature we're launching next week! This will revolutionize how you use our platform.",
        media: "https://source.unsplash.com/random/300x200?tech",
        date: "Today, 09:14",
        status: "active",
        likes: 42,
        comments: [
          {
            id: 1,
            author: {
              name: "Jane Smith",
              avatar: "https://i.pravatar.cc/150?img=11"
            },
            content: "This looks fantastic! When exactly will it be available?",
            date: "Today, 09:30",
            likes: 5,
            replies: []
          },
          {
            id: 2,
            author: {
              name: "Alex Johnson",
              avatar: "https://i.pravatar.cc/150?img=3"
            },
            content: "Will there be documentation available for developers?",
            date: "Today, 09:45",
            likes: 3,
            replies: [
              {
                id: 3,
                author: {
                  name: "John Doe",
                  avatar: "https://i.pravatar.cc/150?img=5"
                },
                content: "Yes, we'll have full API documentation available on launch day.",
                date: "Today, 10:00",
                likes: 2
              }
            ]
          }
        ],
        reports: 0
      },
      {
        id: 2,
        author: {
          name: "Jane Smith",
          avatar: "https://i.pravatar.cc/150?img=11"
        },
        content: "This post contains offensive language and should be removed immediately. I've reported it to the moderators.",
        media: "",
        date: "Today, 10:30",
        status: "reported",
        likes: 0,
        comments: [
          {
            id: 4,
            author: {
              name: "Mike Brown",
              avatar: "https://i.pravatar.cc/150?img=8"
            },
            content: "I agree, this content violates community guidelines.",
            date: "Today, 10:35",
            likes: 2,
            replies: []
          }
        ],
        reports: 5
      },
      {
        id: 3,
        author: {
          name: "Alex Johnson",
          avatar: "https://i.pravatar.cc/150?img=3"
        },
        content: "Just completed my first marathon! Thanks to everyone who supported me along the way. Here's a photo from the finish line.",
        media: "https://source.unsplash.com/random/300x200?sports",
        date: "Yesterday, 16:45",
        status: "active",
        likes: 128,
        comments: [
          {
            id: 5,
            author: {
              name: "Emma Wilson",
              avatar: "https://i.pravatar.cc/150?img=9"
            },
            content: "Congratulations! That's an amazing achievement!",
            date: "Yesterday, 17:00",
            likes: 10,
            replies: []
          },
          {
            id: 6,
            author: {
              name: "David Lee",
              avatar: "https://i.pravatar.cc/150?img=12"
            },
            content: "What was your finishing time?",
            date: "Yesterday, 17:30",
            likes: 3,
            replies: [
              {
                id: 7,
                author: {
                  name: "Alex Johnson",
                  avatar: "https://i.pravatar.cc/150?img=3"
                },
                content: "3 hours 45 minutes! Better than I expected!",
                date: "Yesterday, 18:00",
                likes: 15
              }
            ]
          }
        ],
        reports: 0
      }
    ];

    // DOM elements
    const postsTable = document.getElementById('postsTable');
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');
    const statusFilter = document.getElementById('statusFilter');
    const postDetailModal = new bootstrap.Modal(document.getElementById('postDetailModal'));
    const postDetailContent = document.getElementById('postDetailContent');
    const commentsContent = document.getElementById('commentsContent');

    // Initialize the page
    document.addEventListener('DOMContentLoaded', function() {
      renderPosts(postsData);
      setupEventListeners();
    });

    // Render posts table
    function renderPosts(posts) {
      postsTable.innerHTML = '';
      
      posts.forEach((post, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
          <td>${index + 1}</td>
          <td>
            <div class="d-flex align-items-center gap-2">
              <img src="${post.author.avatar}" class="user-avatar">
              <span>${post.author.name}</span>
            </div>
          </td>
          <td>
            <div class="post-content">${post.content}</div>
          </td>
          <td>
            ${post.media ? `<img src="${post.media}" class="post-image">` : '<span class="text-muted">None</span>'}
          </td>
          <td>${post.date}</td>
          <td>
            <span class="status-badge ${getStatusClass(post.status)}">${post.status.charAt(0).toUpperCase() + post.status.slice(1)}</span>
          </td>
          <td>
            <div class="d-flex gap-2">
              <button class="btn btn-sm btn-outline-primary action-btn view-post-btn" data-post-id="${post.id}">
                <i class="fas fa-eye"></i>
              </button>
              ${post.status === 'reported' ? `
                <button class="btn btn-sm btn-outline-danger action-btn">
                  <i class="fas fa-ban"></i>
                </button>
              ` : ''}
              <button class="btn btn-sm btn-outline-secondary action-btn">
                <i class="fas fa-ellipsis-v"></i>
              </button>
            </div>
          </td>
        `;
        postsTable.appendChild(row);
      });
    }

    // Get status badge class
    function getStatusClass(status) {
      switch(status) {
        case 'active': return 'badge-active';
        case 'reported': return 'badge-reported';
        case 'pending': return 'badge-warning';
        case 'archived': return 'badge-archived';
        default: return '';
      }
    }

    // Setup event listeners
    function setupEventListeners() {
      // Search functionality
      searchBtn.addEventListener('click', performSearch);
      searchInput.addEventListener('keyup', function(e) {
        if (e.key === 'Enter') performSearch();
      });
      statusFilter.addEventListener('change', performSearch);
      
      // View post buttons
      document.addEventListener('click', function(e) {
        if (e.target.closest('.view-post-btn')) {
          const postId = parseInt(e.target.closest('.view-post-btn').getAttribute('data-post-id'));
          const post = postsData.find(p => p.id === postId);
          showPostDetail(post);
        }
      });
    }

    // Perform search
    function performSearch() {
      const searchTerm = searchInput.value.toLowerCase();
      const statusFilterValue = statusFilter.value;
      
      let filteredPosts = postsData;
      
      // Apply status filter
      if (statusFilterValue !== 'all') {
        filteredPosts = filteredPosts.filter(post => post.status === statusFilterValue);
      }
      
      // Apply search filter
      if (searchTerm) {
        filteredPosts = filteredPosts.filter(post => 
          post.content.toLowerCase().includes(searchTerm) ||
          post.author.name.toLowerCase().includes(searchTerm)
        );
      }
      
      renderPosts(filteredPosts);
      
      // Highlight search results
      if (searchTerm) {
        document.querySelectorAll('.post-content, .user-avatar + span').forEach(el => {
          const text = el.textContent.toLowerCase();
          if (text.includes(searchTerm)) {
            const regex = new RegExp(searchTerm, 'gi');
            el.innerHTML = el.textContent.replace(regex, match => 
              `<span class="search-highlight">${match}</span>`
            );
          }
        });
      }
    }

    // Show post detail modal
    function showPostDetail(post) {
      // Render post content
      postDetailContent.innerHTML = `
        <div class="row">
          <div class="col-md-8">
            <div class="d-flex align-items-center mb-3">
              <img src="${post.author.avatar}" class="user-avatar me-3">
              <div>
                <h5 class="mb-0">${post.author.name}</h5>
                <small class="text-muted">Posted on ${post.date}</small>
              </div>
            </div>
            
            <div class="mb-3">
              <p>${post.content}</p>
            </div>
            
            ${post.media ? `
            <div class="mb-3">
              <img src="${post.media}" class="img-fluid rounded">
            </div>
            ` : ''}
            
            <div class="d-flex gap-3 mb-3">
              <span class="text-muted"><i class="fas fa-heart me-1"></i> ${post.likes} likes</span>
              <span class="text-muted"><i class="fas fa-comment me-1"></i> ${post.comments.length} comments</span>
              ${post.reports > 0 ? `<span class="text-danger"><i class="fas fa-flag me-1"></i> ${post.reports} reports</span>` : ''}
            </div>
          </div>
          <div class="col-md-4">
            <div class="card">
              <div class="card-header">
                <h6 class="mb-0">Post Details</h6>
              </div>
              <div class="card-body">
                <div class="mb-3">
                  <h6>Status</h6>
                  <span class="status-badge ${getStatusClass(post.status)}">
                    ${post.status.charAt(0).toUpperCase() + post.status.slice(1)}
                  </span>
                </div>
                
                <div class="mb-3">
                  <h6>Visibility</h6>
                  <span>Public</span>
                </div>
                
                <div class="mb-3">
                  <h6>Post ID</h6>
                  <span>#POST-${post.id.toString().padStart(4, '0')}</span>
                </div>
                
                ${post.status === 'reported' ? `
                <div>
                  <h6>Report Reasons</h6>
                  <ul class="list-group">
                    <li class="list-group-item">Offensive language (3 reports)</li>
                    <li class="list-group-item">Spam (2 reports)</li>
                  </ul>
                </div>
                ` : ''}
              </div>
            </div>
          </div>
        </div>
      `;
      
      // Render comments
      renderComments(post.comments);
      
      postDetailModal.show();
    }

    // Render comments with nested replies
    function renderComments(comments) {
      commentsContent.innerHTML = '';
      
      if (comments.length === 0) {
        commentsContent.innerHTML = `
          <div class="text-center py-4">
            <i class="fas fa-comment-slash fa-2x text-muted mb-3"></i>
            <h5>No Comments Yet</h5>
            <p class="text-muted">This post has no comments</p>
          </div>
        `;
        return;
      }
      
      const container = document.createElement('div');
      container.className = 'comment-container';
      
      comments.forEach(comment => {
        // Main comment
        const commentElement = document.createElement('div');
        commentElement.className = 'comment-item';
        commentElement.innerHTML = `
          <div class="comment-header">
            <img src="${comment.author.avatar}" class="comment-avatar">
            <div class="comment-meta">
              <h6 class="comment-author mb-0">${comment.author.name}</h6>
              <small class="comment-time">${comment.date}</small>
            </div>
            <div class="comment-actions">
              <button class="comment-action-btn"><i class="fas fa-heart"></i> ${comment.likes}</button>
              <button class="comment-action-btn"><i class="fas fa-flag"></i></button>
              <button class="comment-action-btn"><i class="fas fa-trash"></i></button>
            </div>
          </div>
          <div class="comment-body mt-2">
            <p>${comment.content}</p>
          </div>
        `;
        
        container.appendChild(commentElement);
        
        // Replies
        if (comment.replies && comment.replies.length > 0) {
          const repliesContainer = document.createElement('div');
          repliesContainer.style.marginLeft = '30px';
          repliesContainer.style.marginTop = '10px';
          
          comment.replies.forEach(reply => {
            const replyElement = document.createElement('div');
            replyElement.className = 'comment-item';
            replyElement.innerHTML = `
              <div class="comment-header">
                <img src="${reply.author.avatar}" class="comment-avatar">
                <div class="comment-meta">
                  <h6 class="comment-author mb-0">${reply.author.name}</h6>
                  <small class="comment-time">${reply.date}</small>
                </div>
                <div class="comment-actions">
                  <button class="comment-action-btn"><i class="fas fa-heart"></i> ${reply.likes}</button>
                  <button class="comment-action-btn"><i class="fas fa-flag"></i></button>
                  <button class="comment-action-btn"><i class="fas fa-trash"></i></button>
                </div>
              </div>
              <div class="comment-body mt-2">
                <p>${reply.content}</p>
              </div>
            `;
            
            repliesContainer.appendChild(replyElement);
          });
          
          container.appendChild(repliesContainer);
        }
      });
      
      commentsContent.appendChild(container);
    }