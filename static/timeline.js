gsap.registerPlugin(ScrollTrigger)

// get elements that are needed for animating the months and years from home page and entries on scrollMy.html page

//get element that contains elements that will scroll on Scrollmy.html page
let scrll = document.querySelector(".panel");

//get the inner window width to be used in determining end posisitions of animations
let wndw=window.innerWidth;
console.log("wndw", wndw);

//get boxes that will be triggering animations and animated elements themselves
let box = gsap.utils.toArray(".box-2");
let boxes = gsap.utils.toArray(".boxes");
console.log(boxes);
console.log(box);
console.log(box.length);

//define timeline of animated elements and the trigger that will set off animations for months and years on homepage
       let tl = gsap.timeline({
        scrollTrigger: {trigger: ".boxes",
            start: "bottom 30%",
            end: "top 10%",
            markers: false,
            scrub: true,
            pin: true,
            toggleActions: "play complete reverse reset"
                }
        });
            tl.fromTo(".box-2",{autoAlpha:0,y:-100},{
                duration:5,
                ease: "none",
                y: "+=1",
                x: "+=0",
                stagger: 1,
                autoAlpha:1,
                scale:2,
             });
             tl.fromTo(".box-1",{autoAlpha: 0,scale:0,x:0,y:
            -500},{
              duration:3,
              ease: "none",
              y: "+=550",
              x:"+=0",
              stagger: 2,
              autoAlpha: 1,
              rotation: 360,
              scale: 1,
             },"-=1");
             tl.fromTo(".h1",{autoAlpha: 0,scale:0,x:+250,y:
                +550},{
                  duration:1,
                  ease: "none",
                  y: "-=350",
                  x:"-=250",
                  stagger: 2,
                  autoAlpha: 1,
                  scale: 1,
                 });
                 tl.fromTo(".box-3",{autoAlpha:0,scale:0,x:+250,y:
                    +550},{
                      duration:1,
                      ease: "none",
                      y: "-=350",
                      x: "-=250",
                      stagger: 1,
                      autoAlpha: 1,
                      scale: 1,
                     });

//helps to get more granular start and end positions of scrolls for ScrollMy page and the entries that will be scrolled. This is called from the "tween" timeline below
function getScrollAmount(){
  let scrllw = (scrll.offsetWidth);
  let wndwadj = scrllw+(wndw/3);
  console.log("function called", wndwadj);
  return wndwadj;
};

//define timeline of animated elements and the trigger that will set off animations for journal entries on ScrollMy page
let tween= gsap.timeline({
scrollTrigger: {
    trigger: ".panel",
    start: "top 25%%",
    end: ()=>`+=${getScrollAmount()}`,
    markers:false,
    scrub: 2,
    pin: true,
    invalidateOnRefresh:true,
    toggleActions: "play none reverse reset",
      }
      });
      tween.to(".h3",{
        ease: "none",
        duration:1,
        opacity:0,
          });
    tween.fromTo(".box-4",{opacity:.5,x:+wndw,y:'-=20'},{
      ease: "none",
      duration:2,
      x:()=>`-=${getScrollAmount()}`,
      stagger: 0,
      opacity:1,
        });



//used by event on home page when a month is selected beneath parent year..when passed a month and year, return in date format the first day of that month and year. That date will be used in a query in app.py to either default entry page to a date or to query entries in month based on the date.
function monthdayyr(x,y) {
  console.log("this is x", x);
  console.log("this is x", y);
  var obj = {"Jan":'0',"Feb":'1',"Mar":'2',"Apr":'3',"May":'4',"Jun":'5',"Jul":'6',"Aug":'7',"Sep":'8','Oct':'9',"Nov":'10',"Dec":'11'};
  month=obj[x];
  console.log("this is month", month);
  Yr=y;
  d=new Date(y,month,'01');
  month = '' + (d.getMonth() + 1),
    day = '' + d.getDate(),
    year = d.getFullYear();

  if (month.length < 2)
    month = '0' + month;
  if (day.length < 2)
    day = '0' + day;

    vardate= [year, month, day].join('-');

  return vardate;
  console.log("vardate",vardate);
                  };

//handle calendar date change by re-rendering modal with selected date
var myModal = new bootstrap.Modal(document.getElementById('myModal'))
document.getElementById('entrydate').addEventListener('change', function() {
let changevalue=this.value;
console.log("date was changed",changevalue)
  myModal.show();
  modaldateinput=document.getElementById('entrydate');
  modalinput=document.getElementById('historymodal');
  console.log("modal input from funct", modalinput)
  console.log("myModalbutton from funct", document.getElementById('historymodal'));
  defaultdate = changevalue
  console.log("date i got from funct",defaultdate);
  modalinput.value=defaultdate;
  modaldateinput.value=defaultdate;
});




