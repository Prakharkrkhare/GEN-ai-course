function addTask(){ 
  var input = document.getElementById('new-task');
  var taskText = input.value.trim(); 
  if(!taskText) return; 
  var ul = document.getElementById('task-list'); 
  var li = document.createElement('li'); 
  li.textContent = taskText; 
  li.onclick = function() { 
    li.classList.toggle('completed'); 
  };
  var delBtn = document.createElement('button'); 
  delBtn.textContent = 'Delete'; 
  delBtn.onclick = function(e) { 
    e.stopPropagation(); ul.removeChild(li); 
  };  
  li.appendChild(delBtn); 
  ul.appendChild(li); input.value = ''; 
}
document.getElementById('new-task').addEventListener('keyup', function(e) {
   if(e.key === 'Enter') addTask(); 
  }
); 
