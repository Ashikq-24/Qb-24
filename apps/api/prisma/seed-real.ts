import { PrismaClient } from "@prisma/client";
import * as fs from "fs";
import * as path from "path";

const prisma = new PrismaClient();

async function main() {
  const jsonPath = path.resolve(__dirname, "../../../data/real/real_scenario.json");
  if (!fs.existsSync(jsonPath)) {
    throw new Error(`Real scenario JSON not found at ${jsonPath}. Run data/real/build_real_scenario.py first.`);
  }

  const s = JSON.parse(fs.readFileSync(jsonPath, "utf-8"));
  console.log(`Loading Real Indian Railways Scenario: ${s.scenario.name} (seed ${s.scenario.seed})...`);

  // Clear previous scenario if present
  const existing = await prisma.planningScenario.findFirst({ where: { id: s.scenario.id } });
  if (existing) {
    console.log(`Removing existing scenario ${existing.id}...`);
    const oldPlans = await prisma.plan.findMany({ where: { scenarioId: existing.id }, select: { id: true } });
    const oldPlanIds = oldPlans.map((p) => p.id);
    const oldRevisions = await prisma.planRevision.findMany({ where: { planId: { in: oldPlanIds } }, select: { id: true } });
    const oldRevisionIds = oldRevisions.map((r) => r.id);
    await prisma.approvalDecision.deleteMany({ where: { planRevisionId: { in: oldRevisionIds } } });
    await prisma.validationRun.deleteMany({ where: { planRevisionId: { in: oldRevisionIds } } });
    await prisma.simulationRun.deleteMany({ where: { planRevisionId: { in: oldRevisionIds } } });
    await prisma.planTask.deleteMany({ where: { planRevisionId: { in: oldRevisionIds } } });
    await prisma.planBlock.deleteMany({ where: { planRevisionId: { in: oldRevisionIds } } });
    await prisma.planningRun.updateMany({ where: { scenarioId: existing.id }, data: { resultPlanId: null } });
    await prisma.planRevision.deleteMany({ where: { id: { in: oldRevisionIds } } });
    await prisma.plan.deleteMany({ where: { id: { in: oldPlanIds } } });
    await prisma.planningRun.deleteMany({ where: { scenarioId: existing.id } });

    const oldRequests = await prisma.maintenanceRequest.findMany({
      where: { scenarioId: existing.id },
      select: { id: true },
    });
    const oldRequestIds = oldRequests.map((r) => r.id);
    await prisma.maintenanceRequestResource.deleteMany({
      where: { maintenanceRequestId: { in: oldRequestIds } },
    });
    await prisma.requestDependency.deleteMany({
      where: { OR: [{ predecessorId: { in: oldRequestIds } }, { successorId: { in: oldRequestIds } }] },
    });
    await prisma.maintenanceRequest.deleteMany({ where: { scenarioId: existing.id } });
    await prisma.blockWindow.deleteMany({ where: { scenarioId: existing.id } });
    await prisma.trainMovement.deleteMany({ where: { scenarioId: existing.id } });
    await prisma.scenarioEvent.deleteMany({ where: { scenarioId: existing.id } });
    await prisma.planningScenario.delete({ where: { id: existing.id } });
  }

  console.log("Loading real reference network data...");
  await prisma.division.createMany({ data: s.divisions, skipDuplicates: true });
  await prisma.station.createMany({ data: s.stations, skipDuplicates: true });
  await prisma.corridor.createMany({ data: s.corridors, skipDuplicates: true });
  await prisma.corridorSegment.createMany({ data: s.segments, skipDuplicates: true });
  await prisma.trackResource.createMany({ data: s.trackResources, skipDuplicates: true });
  await prisma.asset.createMany({
    data: s.assets.map((a: any) => ({
      ...a,
      installDate: new Date(a.installDate),
      lastMaintenanceDate: a.lastMaintenanceDate ? new Date(a.lastMaintenanceDate) : null,
    })),
    skipDuplicates: true,
  });

  console.log("Creating planning scenario...");
  await prisma.planningScenario.create({
    data: {
      id: s.scenario.id,
      name: s.scenario.name,
      seed: s.scenario.seed,
      description: s.scenario.description,
      configVersion: s.scenario.configVersion,
      generatedAt: new Date(s.scenario.generatedAt),
    },
  });

  console.log(`Loading ${s.maintenanceRequests.length} maintenance requests...`);
  for (const r of s.maintenanceRequests) {
    await prisma.maintenanceRequest.create({
      data: {
        id: r.id,
        requestNumber: r.requestNumber,
        department: r.department,
        assetId: r.assetId,
        corridorId: r.corridorId,
        segmentId: r.segmentId,
        workType: r.workType,
        description: r.description,
        criticality: r.criticality,
        urgency: r.urgency,
        dueDate: new Date(r.dueDate),
        estimatedDurationMinutes: r.estimatedDurationMinutes,
        requiredIsolation: r.requiredIsolation,
        requiredPower: r.requiredPower,
        status: r.status as never,
        scenarioId: s.scenario.id,
        requiredResources: {
          create: r.requiredResources.map((rr: any) => ({
            trackResourceId: rr.trackResourceId,
            quantity: rr.quantity,
          })),
        },
      },
    });
  }

  console.log(`Loading ${s.requestDependencies.length} request dependencies...`);
  for (const dep of s.requestDependencies) {
    await prisma.requestDependency.create({
      data: { predecessorId: dep.predecessorId, successorId: dep.successorId },
    });
  }

  console.log(`Loading explicit compatibility rules...`);
  await prisma.taskCompatibilityRule.deleteMany({});
  await prisma.taskCompatibilityRule.createMany({
    data: s.taskCompatibilityRules.map((rule: any) => ({
      workTypeA: rule.workTypeA,
      workTypeB: rule.workTypeB,
      department: rule.department,
      compatible: rule.compatible,
      reason: rule.reason,
    })),
    skipDuplicates: true,
  });

  console.log(`Loading ${s.blockWindows.length} block windows...`);
  await prisma.blockWindow.createMany({
    data: s.blockWindows.map((w: any) => ({
      ...w,
      startTime: new Date(w.startTime),
      endTime: new Date(w.endTime),
      scenarioId: s.scenario.id,
    })),
    skipDuplicates: true,
  });

  console.log(`Loading ${s.trainMovements.length} real train movements...`);
  await prisma.trainMovement.createMany({
    data: s.trainMovements.map((t: any) => ({
      ...t,
      scheduledStart: new Date(t.scheduledStart),
      scheduledEnd: new Date(t.scheduledEnd),
      scenarioId: s.scenario.id,
    })),
    skipDuplicates: true,
  });

  console.log(`Loading ${s.scenarioEvents.length} scenario events...`);
  await prisma.scenarioEvent.createMany({
    data: s.scenarioEvents.map((e: any) => ({
      id: e.id,
      eventType: e.eventType,
      source: e.source,
      payload: e.payload as object,
      scenarioId: s.scenario.id,
    })),
    skipDuplicates: true,
  });

  console.log(`\nDONE! Real Indian Railways Scenario ${s.scenario.id} successfully loaded into PostgreSQL.`);
}

main()
  .catch((err) => {
    console.error(err);
    process.exitCode = 1;
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
