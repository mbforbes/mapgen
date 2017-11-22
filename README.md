# mapgen
wip graphics prj

## relwork

### General

**Modeling the Appearance and Behavior of Urban Spaces** _(Vanegas et al., 2009)_ [[pdf](https://pdfs.semanticscholar.org/2fa5/555bd7300b7383e62b489169db3dd460533d.pdf)]

Overview. Breaks problems into "Layout Modeling" (road networks + land use
labels) (my focus), "Building Modeling" (3D geometry of buildings), and "Facade
Modeling" (3D facades + textures).

### Layout Modeling

**Interactive Geometric Simulation of 4D Cities** _(Weber et al., 2009)_ [[pdf](http://peterwonka.net/Publications/pdfs/2009.EG.Weber.UrbanSimulation.FinalVersion.pdf)]

Simulation of a 3D city growing over time.

**[Purdue group](https://www.cs.purdue.edu/cgvlab/urban/urban-procedural-modeling.html) w/ several relevant papers**

Some more details are below.

**Example-Driven Procedural Urban Roads** _(Nishida et al., 2015)_ [[pdf](https://www.cs.purdue.edu/cgvlab/papers/aliaga/cgf15.pdf)]

Tool for editing road networks.

**Procedural Generation of Parcels in Urban Modeling** _(Vanegas et al., 2012)_ [[pdf](https://www.cs.purdue.edu/cgvlab/papers/aliaga/eg2012.pdf)]

Algorithms for automatically splitting blocks (spaces inbetween a road network)
into parcels.

**Interactive Example-Based Urban Layout Synthesis** _(Aliaga et al., 2008)_

Given an example image, synthesize a street network and copy and paste aerial
pictures into them.

**Interactive Reconfiguration of Urban Layouts** _(Aliaga et al., 2008)_

A tool to made edits to an urban layout and regenerate / conform the roads /
parcels / images to look nice again.

### Learning

**A Probabilistic Model for Exteriors of Residential Buildings** _(Fan and Wonka, 2016)_ [[pdf](https://dl.acm.org/citation.cfm?id=2910578)] [[prj](https://sites.google.com/site/lubinfan/publications/2016-bldg-exteriors-model)]

Learn a GM for 3D buildings and facades.

**Inverse Procedural Modeling of Facade Layouts** _(Wu et al., 2014)_ [[pdf](http://peterwonka.net/Publications/pdfs/2014.SG.Wu.InverseFacadeModeling.pdf)]

Learn (I think) a split grammar for facades, preferring shorter descriptions.

**Bayesian Grammar Learning for Inverse Procedural Modeling** _(Martinovic and Gool, 2013)_ [[pdf](http://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=6618877)]

Learn a 2D CFG from a set of labeled facades.

**A Probabilistic Model for Component-Based Shape Synthesis** _(Kalogerakis et al., 2012)_ [[pdf](http://people.cs.umass.edu/~kalo/papers/ShapeSynthesis/ShapeSynthesis.pdf)]

Learn GM on shapes and generate their own (shapes like dinosaur, chair, boat).

**Inverse Procedural Modeling by Automatic Generation of L-systems** _(Stava et al., 2010)_ [[pdf](http://hpcg.purdue.edu/papers/Stava10EG.pdf)]

(Not actually learning, I think) Constructs an L-system from a 2D vector image.

**Detecting and Parsing Architecture at City Scale from Range Data** _(Toshev et al., 2010)_ [[pdf](http://repository.upenn.edu/cgi/viewcontent.cgi?article=1539&context=cis_papers)]

Learn to parse point clouds to tree of roofs.
