/** Retain reviewed teacher, education and curriculum links during older build stages. */
const connection = /<section\b[^>]*\bid="(teacher-connection|education-info-links|curriculum-connection)"[^>]*>[\s\S]*?<\/section>/g;
const schema = /(<script\b[^>]*type=["']application\/ld\+json["'][^>]*>)([\s\S]*?)(<\/script>)/gi;
const pageTypes = new Set(['WebPage', 'CollectionPage', 'Article']);
function visit(value, fn) {
  if (!value || typeof value !== 'object') return;
  if (Array.isArray(value)) { value.forEach(item => visit(item, fn)); return; }
  fn(value); Object.values(value).forEach(item => visit(item, fn));
}
export function laterDate(current, reviewed) {
  return /^\d{4}-\d{2}-\d{2}$/.test(current || '') && current > reviewed ? current : reviewed;
}
export function preserveTeacherContent(before, after) {
  const sections = [...before.matchAll(connection)];
  if (!sections.length || before === after) return after;
  if (new Set(sections.map(section => section[1])).size !== sections.length)
    throw Error('Unexpected duplicate content connection');
  const kept = sections.map(section => section[0]).join('');
  let next = after.replace(connection, '');
  if (!next.includes('</main>')) throw Error('Missing main for content connection');
  const main = /<main\b[^>]*>[\s\S]*?<\/main>/;
  const originalMain = before.match(main)?.[0];
  const generatedMain = next.match(main)?.[0];
  // When the underlying body is unchanged, keep the reviewed links in their
  // original places near the hero instead of moving them below long images.
  if (originalMain && originalMain.replace(connection, '') === generatedMain)
    next = next.replace(main, originalMain);
  else next = next.replace('</main>', kept + '</main>');
  const dates = new Map();
  for (const match of before.matchAll(schema)) visit(JSON.parse(match[2]), node => {
    if ([].concat(node['@type'] || []).some(type => pageTypes.has(type)) && node['@id'])
      dates.set(node['@id'], node.dateModified);
  });
  next = next.replace(schema, (all, start, body, end) => {
    const data=JSON.parse(body); let changed=false;
    visit(data, node => {
      if (!dates.has(node['@id'])) return;
      const date = laterDate(dates.get(node['@id']), node.dateModified);
      if (date !== node.dateModified) { node.dateModified=date; changed=true; }
    });
    return changed ? start + JSON.stringify(data).replaceAll('<','\\u003c') + end : all;
  });
  return next;
}
