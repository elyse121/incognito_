document.addEventListener('DOMContentLoaded', function() {
      // Sample data
      const groupsData = [
        {
          id: 1,
          name: "Marketing Team",
          avatarText: "MT",
          membersCount: 8,
          lastActivity: "Today, 14:30",
          status: "active",
          created: "Jan 15, 2023",
          admin: "John Doe",
          totalMessages: 1243,
          members: [
            {id: 1, name: "John Doe", status: "admin", lastSeen: "Online", avatar: "https://i.pravatar.cc/150?img=5"},
            {id: 2, name: "Jane Smith", status: "active", lastSeen: "Today, 14:25", avatar: "https://i.pravatar.cc/150?img=11"},
            {id: 3, name: "Alex Johnson", status: "active", lastSeen: "Today, 12:40", avatar: "https://i.pravatar.cc/150?img=3"},
            {id: 4, name: "Sarah Miller", status: "muted", lastSeen: "Yesterday, 18:15", avatar: "https://i.pravatar.cc/150?img=4"},
            {id: 5, name: "Mike Brown", status: "banned", lastSeen: "Jul 30, 22:10", avatar: "https://i.pravatar.cc/150?img=8"}
          ],
          messages: [
            {sender: 1, text: "Has everyone reviewed the new campaign?", time: "Today, 14:25"},
            {sender: 2, text: "Yes, looks good to me!", time: "Today, 14:28"},
            {sender: 3, text: "I have some suggestions for the visuals", time: "Today, 14:30"},
            {sender: 5, text: "This is a scam!", time: "Jul 30, 22:05", reported: true}
          ]
        },
        {
          id: 2,
          name: "Development Team",
          avatarText: "DT",
          membersCount: 5,
          lastActivity: "Today, 09:15",
          status: "active",
          created: "Feb 10, 2023",
          admin: "Emma Wilson",
          totalMessages: 876,
          members: [
            {id: 6, name: "Emma Wilson", status: "admin", lastSeen: "Online", avatar: "https://i.pravatar.cc/150?img=9"},
            {id: 7, name: "David Lee", status: "active", lastSeen: "Today, 09:10", avatar: "https://i.pravatar.cc/150?img=12"},
            {id: 3, name: "Alex Johnson", status: "active", lastSeen: "Today, 08:45", avatar: "https://i.pravatar.cc/150?img=3"}
          ],
          messages: [
            {sender: 6, text: "The new update is ready for testing", time: "Today, 09:00"},
            {sender: 7, text: "I'll run the tests this morning", time: "Today, 09:10"},
            {sender: 3, text: "Found a bug in the login flow", time: "Today, 09:15"}
          ]
        },
        {
          id: 3,
          name: "Social Media",
          avatarText: "SM",
          membersCount: 3,
          lastActivity: "Yesterday, 16:45",
          status: "archived",
          created: "Mar 5, 2023",
          admin: "Jane Smith",
          totalMessages: 542,
          members: [
            {id: 2, name: "Jane Smith", status: "admin", lastSeen: "Today, 14:25", avatar: "https://i.pravatar.cc/150?img=11"},
            {id: 8, name: "Lisa Taylor", status: "active", lastSeen: "Yesterday, 16:40", avatar: "https://i.pravatar.cc/150?img=7"},
            {id: 4, name: "Sarah Miller", status: "left", lastSeen: "Aug 1, 16:45", avatar: "https://i.pravatar.cc/150?img=4"}
          ],
          messages: [
            {sender: 2, text: "The Instagram post got 1K likes!", time: "Yesterday, 16:30"},
            {sender: 8, text: "Great engagement! Let's boost it", time: "Yesterday, 16:40"},
            {sender: 2, text: "Agreed, I'll set up the ad", time: "Yesterday, 16:45"}
          ]
        }
      ];
      
      // DOM elements
      const groupsTableBody = document.getElementById('groupsTableBody');
      const membersContainer = document.getElementById('membersContainer');
      const groupMessagesContainer = document.getElementById('groupMessagesContainer');
      const searchInput = document.getElementById('searchInput');
      const searchBtn = document.getElementById('searchBtn');
      const noGroupsResults = document.getElementById('noGroupsResults');
      const noMembersResults = document.getElementById('noMembersResults');
      
      // Current state
      let currentView = 'groups'; // 'groups' or 'groupDetails'
      let currentGroupId = null;
      let currentSearchTerm = '';
      
      // Initialize the app
      function initApp() {
        renderGroupsList(groupsData);
        setupEventListeners();
      }
      
      // Render groups list
      function renderGroupsList(groups) {
        groupsTableBody.innerHTML = '';
        
        if (groups.length === 0) {
          noGroupsResults.classList.remove('d-none');
          return;
        }
        
        noGroupsResults.classList.add('d-none');
        
        groups.forEach(group => {
          const row = document.createElement('tr');
          row.innerHTML = `
            <td>
              <div class="d-flex align-items-center gap-3">
                <div class="group-avatar">${group.avatarText}</div>
                <span class="fw-bold">${group.name}</span>
              </div>
            </td>
            <td>
              <span class="badge bg-light text-dark">${group.membersCount} members</span>
            </td>
            <td>${group.lastActivity}</td>
            <td>
              <span class="badge ${getStatusBadgeClass(group.status)}">
                ${group.status.charAt(0).toUpperCase() + group.status.slice(1)}
              </span>
            </td>
            <td>
              <button class="btn btn-sm btn-outline-primary action-btn view-group-btn" 
                      data-group-id="${group.id}" 
                      data-group-name="${group.name}">
                <i class="fas fa-eye"></i> View
              </button>
              <button class="btn btn-sm btn-outline-danger action-btn">
                <i class="fas fa-ban"></i> Ban
              </button>
            </td>
          `;
          groupsTableBody.appendChild(row);
        });
      }
      
      // Render group details
      function renderGroupDetails(groupId) {
        const group = groupsData.find(g => g.id == groupId);
        if (!group) return;
        
        // Update header info
        document.getElementById('selectedGroupName').textContent = group.name;
        document.getElementById('groupCreatedDate').textContent = group.created;
        document.getElementById('groupAdmin').textContent = group.admin;
        document.getElementById('totalMessages').textContent = group.totalMessages;
        document.getElementById('lastMessageTime').textContent = group.lastActivity;
        
        // Render members
        renderMembersList(group.members);
        
        // Render messages
        renderGroupMessages(group.messages, group.members);
      }
      
      // Render members list
      function renderMembersList(members) {
        membersContainer.innerHTML = '';
        
        let filteredMembers = members;
        if (currentSearchTerm) {
          filteredMembers = members.filter(member => 
            member.name.toLowerCase().includes(currentSearchTerm.toLowerCase())
          );
        }
        
        if (filteredMembers.length === 0) {
          noMembersResults.classList.remove('d-none');
          return;
        }
        
        noMembersResults.classList.add('d-none');
        
        filteredMembers.forEach(member => {
          const memberCard = document.createElement('div');
          memberCard.className = `col-md-6 member-card ${member.status === 'banned' ? 'reported' : ''}`;
          memberCard.innerHTML = `
            <div class="card mb-3">
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-start">
                  <div class="d-flex align-items-center gap-3">
                    <img src="${member.avatar}" class="user-avatar">
                    <div>
                      <h6 class="mb-1 fw-bold">${member.name}</h6>
                      <small class="text-muted">Last seen: ${member.lastSeen}</small>
                    </div>
                  </div>
                  <div class="btn-group">
                    <span class="badge ${getMemberBadgeClass(member.status)} me-2">
                      ${member.status.charAt(0).toUpperCase() + member.status.slice(1)}
                    </span>
                    <button class="btn btn-sm btn-outline-primary">
                      <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger">
                      <i class="fas fa-ban"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-secondary">
                      <i class="fas fa-trash"></i>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          `;
          membersContainer.appendChild(memberCard);
        });
      }
      
      // Render group messages
      function renderGroupMessages(messages, members) {
        groupMessagesContainer.innerHTML = '';
        
        messages.forEach(msg => {
          const sender = members.find(m => m.id == msg.sender);
          if (!sender) return;
          
          const bubble = document.createElement('div');
          bubble.className = `chat-bubble ${msg.reported ? 'reported' : ''}`;
          bubble.innerHTML = `
            <strong>${sender.name}</strong> (${msg.time})<br>
            ${msg.text}
            <div class="message-actions">
              <div class="dropdown">
                <button class="btn btn-sm btn-link text-muted p-0" data-bs-toggle="dropdown">
                  <i class="fas fa-ellipsis-v"></i>
                </button>
                <ul class="dropdown-menu">
                  <li><a class="dropdown-item" href="#"><i class="fas fa-trash me-2"></i>Delete message</a></li>
                  ${msg.reported ? 
                    '<li><a class="dropdown-item text-success" href="#"><i class="fas fa-check me-2"></i>Approve message</a></li>' : 
                    '<li><a class="dropdown-item text-danger" href="#"><i class="fas fa-flag me-2"></i>Report message</a></li>'}
                </ul>
              </div>
            </div>
          `;
          groupMessagesContainer.appendChild(bubble);
        });
      }
      
      // Get status badge class
      function getStatusBadgeClass(status) {
        switch(status) {
          case 'active': return 'bg-success';
          case 'archived': return 'bg-secondary';
          case 'reported': return 'bg-warning text-dark';
          default: return 'bg-secondary';
        }
      }
      
      // Get member badge class
      function getMemberBadgeClass(status) {
        switch(status) {
          case 'admin': return 'bg-primary';
          case 'active': return 'bg-success';
          case 'muted': return 'bg-warning text-dark';
          case 'banned': return 'badge-banned';
          case 'left': return 'bg-secondary';
          default: return 'bg-secondary';
        }
      }
      
      // Search functionality
      function performSearch() {
        currentSearchTerm = searchInput.value.trim();
        
        if (currentView === 'groups') {
          const filteredGroups = groupsData.filter(group => 
            group.name.toLowerCase().includes(currentSearchTerm.toLowerCase())
          );
          renderGroupsList(filteredGroups);
        } else if (currentView === 'groupDetails' && currentGroupId) {
          const group = groupsData.find(g => g.id == currentGroupId);
          if (group) renderMembersList(group.members);
        }
      }
      
      // Setup event listeners
      function setupEventListeners() {
        // Search button click
        searchBtn.addEventListener('click', performSearch);
        
        // Search on Enter key
        searchInput.addEventListener('keyup', function(e) {
          if (e.key === 'Enter') performSearch();
        });
        
        // View group button
        document.addEventListener('click', function(e) {
          if (e.target.closest('.view-group-btn')) {
            const btn = e.target.closest('.view-group-btn');
            currentGroupId = parseInt(btn.getAttribute('data-group-id'));
            currentView = 'groupDetails';
            
            document.querySelector('.group-table').classList.add('d-none');
            document.getElementById('groupDetailsPanel').classList.remove('d-none');
            
            renderGroupDetails(currentGroupId);
          }
        });
        
        // Back to groups list
        document.getElementById('backToGroupsBtn').addEventListener('click', function() {
          currentView = 'groups';
          document.querySelector('.group-table').classList.remove('d-none');
          document.getElementById('groupDetailsPanel').classList.add('d-none');
          renderGroupsList(
            currentSearchTerm 
              ? groupsData.filter(group => group.name.toLowerCase().includes(currentSearchTerm.toLowerCase()))
              : groupsData
          );
        });
      }
      
      // Initialize the application
      initApp();
    });