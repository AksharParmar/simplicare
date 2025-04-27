/* static/calendar.js */
document.addEventListener("DOMContentLoaded", () => {
    /* -------- constants -------- */
    const monthLabel   = document.getElementById("monthLabel");
    const grid         = document.getElementById("calendarGrid");
    const prevBtn      = document.getElementById("prevBtn");
    const nextBtn      = document.getElementById("nextBtn");
  
    const dayNames = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"];
    const today    = new Date();
    let viewYear   = today.getFullYear();
    let viewMonth  = today.getMonth();          // 0-based
  
    /* -------- render helpers -------- */
    function renderCalendar(year, month){
      // clear grid
      grid.innerHTML = "";
  
      // day name header row
      dayNames.forEach(d =>{
        const el = document.createElement("div");
        el.textContent = d;
        el.className = "day-name";
        grid.appendChild(el);
      });
  
      // figure out month stats
      const firstDayIdx = new Date(year, month, 1).getDay();
      const daysInMonth = new Date(year, month+1, 0).getDate();
  
      // blank cells before first day
      for(let i=0;i<firstDayIdx;i++){
        grid.appendChild(document.createElement("div"));
      }
  
      // dates
      for(let d=1; d<=daysInMonth; d++){
        const cell = document.createElement("div");
        cell.textContent = d;
        cell.className = "date";
  
        // highlight today
        if(year===today.getFullYear() && month===today.getMonth() && d===today.getDate()){
          cell.classList.add("date--today");
        }
  
        // click handler
        cell.addEventListener("click",()=>{
          grid.querySelectorAll(".date--selected").forEach(c=>c.classList.remove("date--selected"));
          cell.classList.add("date--selected");
  
          /* TODO: emit event / call API here
             e.g., window.dispatchEvent(new CustomEvent("calendar:select",{detail:{year,month,day:d}}));
             or open a modal to add an appointment
          */
        });
  
        grid.appendChild(cell);
      }
  
      /* label */
      const monthName = new Date(year, month).toLocaleString("default",{month:"long"});
      monthLabel.textContent = `${monthName} ${year}`;
    }
  
    /* -------- navigation -------- */
    prevBtn.addEventListener("click", ()=> {
      viewMonth--;
      if(viewMonth<0){viewMonth=11; viewYear--;}
      renderCalendar(viewYear, viewMonth);
    });
    nextBtn.addEventListener("click", ()=> {
      viewMonth++;
      if(viewMonth>11){viewMonth=0; viewYear++;}
      renderCalendar(viewYear, viewMonth);
    });
  
    /* initial paint */
    renderCalendar(viewYear, viewMonth);
  });
  