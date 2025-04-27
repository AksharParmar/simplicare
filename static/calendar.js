/* static/calendar.js */
document.addEventListener("DOMContentLoaded", () => {
    // DOM refs
    const grid       = document.getElementById("calendarGrid");
    const monthLabel = document.getElementById("monthLabel");
    const prevBtn    = document.getElementById("prevBtn");
    const nextBtn    = document.getElementById("nextBtn");
  
    const btnMonth   = document.getElementById("viewMonthBtn");
    const btnWeek    = document.getElementById("viewWeekBtn");
    const btnDay     = document.getElementById("viewDayBtn");
  
    // state
    const today      = new Date();
    let cursor       = new Date(today);    // date currently "selected"
    let view         = "month";            // month | week | day
  
    /* ========== render helpers ========== */
    function pad(n){return n.toString().padStart(2,"0");}
    function iso(y,m,d){return `${y}-${pad(m+1)}-${pad(d)}`;}  // YYYY-MM-DD
  
    /* ---- MONTH ---- */
    function renderMonth(){
      grid.innerHTML = "";
      grid.parentElement.classList.remove("calendar--week","calendar--day");
  
      // day-name header
      ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"].forEach(d=>{
        const h=document.createElement("div");
        h.textContent=d;h.className="day-name";grid.appendChild(h);
      });
  
      const y=cursor.getFullYear(), m=cursor.getMonth();
      const firstIdx=new Date(y,m,1).getDay();
      const daysInMonth=new Date(y,m+1,0).getDate();
  
      // blanks
      for(let i=0;i<firstIdx;i++) grid.appendChild(document.createElement("div"));
  
      // dates
      for(let d=1;d<=daysInMonth;d++){
        const cell=document.createElement("div");
        cell.className="date";
        cell.textContent=d;
  
        if(y===today.getFullYear() && m===today.getMonth() && d===today.getDate())
            cell.classList.add("date--today");
        if(d===cursor.getDate()) cell.classList.add("date--selected");
  
        cell.onclick=()=>{cursor.setDate(d);view="day";paint();}
        grid.appendChild(cell);
      }
  
      monthLabel.textContent = cursor.toLocaleString("default",{month:"long",year:"numeric"});
    }
  
    /* ---- WEEK ---- */
    function renderWeek(){
      grid.innerHTML="";grid.parentElement.classList.add("calendar--week");
      // snap cursor to Sunday of the week
      const start=new Date(cursor);
      start.setDate(cursor.getDate()-cursor.getDay());
  
      for(let i=0;i<7;i++){
        const d=new Date(start);d.setDate(start.getDate()+i);
        const cell=document.createElement("div");
        cell.className="date";
        cell.innerHTML=`<div class="week-label">${d.toLocaleString("default",{weekday:"short"})}</div>${d.getDate()}`;
        if(+d===+today) cell.classList.add("date--today");
        if(d.getDate()===cursor.getDate() && d.getMonth()===cursor.getMonth()) cell.classList.add("date--selected");
        cell.onclick=()=>{cursor=new Date(d);view="day";paint();}
        grid.appendChild(cell);
      }
  
      monthLabel.textContent = `${start.toLocaleDateString(undefined,{month:"short",day:"numeric"})} – ${cursor.toLocaleDateString(undefined,{month:"short",day:"numeric",year:"numeric"})}`;
    }
  
    /* ---- DAY ---- */
    function renderDay(){
      grid.innerHTML="";grid.parentElement.classList.add("calendar--day");
      // 24 slots
      for(let h=0;h<24;h++){
        const slot=document.createElement("div");
        slot.className="date time-slot";
        slot.textContent=`${h.toString().padStart(2,"0")}:00`;
        slot.onclick=()=>alert(`Add event on ${iso(cursor.getFullYear(),cursor.getMonth(),cursor.getDate())} at ${h}:00`);
        grid.appendChild(slot);
      }
      monthLabel.textContent = cursor.toLocaleDateString(undefined,{weekday:"long",month:"long",day:"numeric",year:"numeric"});
    }
  
    /* ---- dispatcher ---- */
    function paint(){
      // clean view-switch highlight
      [btnMonth,btnWeek,btnDay].forEach(b=>b.classList.remove("active"));
      if(view==="month") {btnMonth.classList.add("active");renderMonth();}
      if(view==="week")  {btnWeek.classList.add("active"); renderWeek();}
      if(view==="day")   {btnDay.classList.add("active");  renderDay();}
    }
  
    /* ========== navigation buttons ========== */
    function shift(delta){
      if(view==="month"){
        cursor.setMonth(cursor.getMonth()+delta);
      }else if(view==="week"){
        cursor.setDate(cursor.getDate()+7*delta);
      }else{ // day
        cursor.setDate(cursor.getDate()+delta);
      }
      paint();
    }
    prevBtn.onclick=()=>shift(-1);
    nextBtn.onclick=()=>shift(1);
  
    /* ========== view-switch buttons ========== */
    btnMonth.onclick=()=>{view="month";paint();};
    btnWeek .onclick=()=>{view="week"; paint();};
    btnDay  .onclick=()=>{view="day";  paint();};
  
    /* first draw */
    paint();
  });
  