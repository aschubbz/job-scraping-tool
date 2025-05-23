import fs from "fs";
// Helper function to safely parse a float value
function parseFloatSafe(x) {
  const num = parseFloat(x);
  return isNaN(num) ? null : num;
}
// Helper function to calculate average of an array
function average(arr) {
  if (!arr.length) return 0;
  const sum = arr.reduce((acc, val) => acc + val, 0);
  return sum / arr.length;
}
// Function to calculate the earliest date, latest date, and duration in days
function calculateDateStats(data) {
  const dates = data.map(item => new Date(item.createTime));
  const earliest = new Date(Math.min(...dates));
  const latest = new Date(Math.max(...dates));
  const durationMs = latest - earliest;
  const durationDays = durationMs / (1000 * 60 * 60 * 24);
  return { earliest, latest, durationDays };
}
const feedName = "new-job-feed.js";
let jobFeed = JSON.parse(fs.readFileSync(feedName));
console.log(`Read ${jobFeed.length} jobs`);
// Remove duplicated job with same id
jobFeed = jobFeed.filter((job, index, self) => self.findIndex(t => t.id === job.id) === index);
console.log(`Duplicated removed - now ${jobFeed.length} jobs`);
// Save the deduplicated job feed
fs.writeFileSync(feedName, JSON.stringify(jobFeed, null, 2));
// Filter low paying jobs - under $45
jobFeed = jobFeed.filter(job => !job.jobTile.job.hourlyBudgetMax || parseFloat(job.jobTile.job.hourlyBudgetMax) > 49);
console.log(`Filtered ${jobFeed.length} jobs`);
// Filter new payment not verified clients without budget range
jobFeed = jobFeed.filter(job => {
  return !job.jobTile.job.hourlyBudgetMax ? job.upworkHistoryData.client.totalReviews > 0 && job.upworkHistoryData.client.paymentVerificationStatus : true;
});
console.log(`Filtered ${jobFeed.length} jobs`);
// Create summary of job feed
const summary = jobFeed.map(job => ({
  title: job.title,
  skills: job.ontologySkills.map(({ prettyName }) => prettyName),
  clientSpent: job.upworkHistoryData.client.totalSpent?.amount,
  clientReviews: job.upworkHistoryData.client.totalReviews,
  minHourly: job.jobTile.job.hourlyBudgetMin,
  maxHourly: job.jobTile.job.hourlyBudgetMax,
  totalApplicants: job.jobTile.job.totalApplicants,
  durationWeeks: job.jobTile.job.hourlyEngagementDuration?.weeks,
  expertLevel: job.jobTile.job.contractorTier,
  paymentVerified: job.upworkHistoryData.client.paymentVerificationStatus,
  createTime: job.jobTile.job.publishTime
}));
fs.writeFileSync(feedName + "-summary.json", JSON.stringify(summary, null, 2));
const jobsPartial = summary;
const processedJobsPartial = [];
// Process jobs partial
for (const job of jobsPartial) {
  const cs = parseFloatSafe(job.clientSpent !== undefined ? job.clientSpent : 0);
  let minH = parseFloatSafe(job.minHourly);
  let maxH = parseFloatSafe(job.maxHourly);
  // // Apply missing rate logic
  // if (minH === null || maxH === null) {
  //   if (cs !== null && cs > 10000) {
  //     minH = 30.0;
  //     maxH = 70.0;
  //   } else {
  //     minH = 15.0;
  //     maxH = 30.0;
  //   }
  // }
  processedJobsPartial.push({
    title: job.title,
    skills: job.skills || [],
    clientSpent: cs,
    clientReviews: job.clientReviews != null ? job.clientReviews : 0,
    minHourly: minH,
    maxHourly: maxH,
    totalApplicants: job.totalApplicants != null ? job.totalApplicants : 0,
    durationWeeks: job.durationWeeks != null ? job.durationWeeks : 0,
    expertLevel: job.expertLevel,
    paymentVerified: job.paymentVerified === 'VERIFIED'
  });
}
// Create an object to hold aggregated skill data
const skillData = {};
// Initialize skill data if not existing
for (const job of processedJobsPartial) {
  for (const skill of job.skills) {
    if (!skillData[skill]) {
      skillData[skill] = {
        count: 0,
        minHourly: [],
        maxHourly: [],
        applicants: [],
        duration: [],
        verified_count: 0
      };
    }
    const d = skillData[skill];
    d.count += 1;
    d.minHourly.push(job.minHourly);
    d.maxHourly.push(job.maxHourly);
    d.applicants.push(job.totalApplicants);
    d.duration.push(job.durationWeeks);
    if (job.paymentVerified) {
      d.verified_count += 1;
    }
  }
}
// Run the function on the JSON array
const stats = calculateDateStats(summary);
// Build a list of skill statistics
const skillStatsList = [];
for (const [skill, d] of Object.entries(skillData)) {
  const c = d.count;
  const avg_min = d.minHourly.length ? average(d.minHourly) : 0;
  const avg_max = d.maxHourly.length ? average(d.maxHourly) : 0;
  const avg_app = d.applicants.length ? average(d.applicants) : 0;
  const avg_dur = d.duration.length ? average(d.duration) : 0;
  const verified_ratio = c ? d.verified_count / c : 0;
  skillStatsList.push({
    skill: skill,
    count: parseInt(c*10 / stats.durationDays)/10,
    avg_min: parseInt(avg_min),
    avg_max: parseInt(avg_max),
    avg_applicants: parseInt(avg_app),
    avg_duration: parseInt(avg_dur),
  });
}
// Sort the list based on multiple criteria
skillStatsList.sort((a, b) => {
  if (b.count !== a.count) return b.count - a.count;
  if (b.avg_max !== a.avg_max) return b.avg_max - a.avg_max;
  if (a.avg_applicants !== b.avg_applicants) return a.avg_applicants - b.avg_applicants;
  return b.avg_duration - a.avg_duration;
});
// Save top30partial to csv file
const csvHeader = "Skill,Jobs,Min,Max,Applicants,Weeks,Payment Verified %\n";
const csvContent = skillStatsList.map(e => Object.values(e).join(",")).join("\n");
// Output the results
fs.writeFileSync("top30.csv", "Earliest Date:" + stats.earliest.toISOString() + "\n");
fs.appendFileSync("top30.csv", "Latest Date:" + stats.latest.toISOString() + "\n");
fs.appendFileSync("top30.csv", "Duration in Days:" + stats.durationDays + "\n");
fs.appendFileSync("top30.csv", csvHeader + csvContent);